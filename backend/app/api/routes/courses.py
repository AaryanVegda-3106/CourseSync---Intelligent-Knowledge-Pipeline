"""
CourseSync — API Routes for Courses

All endpoints per PRD §10, using Pydantic request/response schemas
and the consistent error envelope.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, CourseSyncError
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseListResponse,
    CourseHierarchy,
    IngestionJobResponse,
    IngestRequest,
    ExportFile,
    ExportListResponse,
    CourseStatus,
)
from app.schemas.errors import ErrorResponse
from app.repositories.course_repository import CourseRepository
from app.repositories.content_repository import ContentRepository
from app.services.firecrawl_service import FirecrawlService
from app.services.discovery_service import DiscoveryService
from app.services.hierarchy_service import HierarchyService
from app.services.ingestion_service import IngestionService
from app.services.processing_service import ProcessingService
from app.services.export_service import ExportService
from app.services.storage_service import StorageService
from app.services.llm import create_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/courses", tags=["courses"])

# ── Dependency instances (singleton-ish for MVP) ─────────

_course_repo = CourseRepository()
_content_repo = ContentRepository()
_storage = StorageService()
_discovery = DiscoveryService()
_hierarchy = HierarchyService()


def _get_firecrawl() -> FirecrawlService:
    settings = get_settings()
    return FirecrawlService(api_key=settings.firecrawl_api_key)


def _get_ingestion() -> IngestionService:
    return IngestionService(
        firecrawl=_get_firecrawl(),
        storage=_storage,
        course_repo=_course_repo,
        content_repo=_content_repo,
    )


def _get_processing() -> ProcessingService:
    llm = create_llm_provider()
    return ProcessingService(
        llm=llm,
        storage=_storage,
        course_repo=_course_repo,
        content_repo=_content_repo,
    )


def _get_export() -> ExportService:
    return ExportService(
        storage=_storage,
        course_repo=_course_repo,
        content_repo=_content_repo,
    )


# ── POST /api/courses ───────────────────────────────────

@router.post("", response_model=CourseResponse, status_code=201)
async def create_course(data: CourseCreate):
    """Create a new course record."""
    # Basic URL validation (FR-20.3)
    url = data.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=422, detail="URL must start with http:// or https://")

    course = await _course_repo.create_course(data)
    return course


# ── GET /api/courses ────────────────────────────────────

@router.get("", response_model=CourseListResponse)
async def list_courses():
    """List all courses."""
    courses = await _course_repo.list_courses()
    return CourseListResponse(courses=courses, total=len(courses))


# ── GET /api/courses/{id} ──────────────────────────────

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str):
    """Get a single course."""
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.delete("/{course_id}", status_code=204)
async def delete_course(course_id: str):
    """Delete a course and all associated data."""
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Delete from DB (foreign keys ON DELETE CASCADE will handle modules, pages, etc.)
    deleted = await _course_repo.delete_course(course_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete course")
        
    # Delete physical files
    _storage.delete_course(course_id)
    return None


# ── POST /api/courses/{id}/discover ─────────────────────

@router.post("/{course_id}/discover", response_model=CourseHierarchy)
async def discover_course(course_id: str):
    """Run Firecrawl Map + discovery heuristics on a course URL.

    Returns the discovered hierarchy for user review before scraping (FR-2.5).
    """
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    await _course_repo.update_course_status(course_id, CourseStatus.DISCOVERING)

    try:
        # Step 1: Map URLs via Firecrawl (FR-2.1)
        firecrawl = _get_firecrawl()
        map_result = await firecrawl.map_course(course.url)

        if not map_result.success:
            raise HTTPException(
                status_code=502,
                detail=f"Firecrawl Map failed: {map_result.error}",
            )

        # Step 2: Filter and classify URLs deterministically (FR-2.2, FR-2.3)
        classified_pages = _discovery.discover(course.url, map_result.links)

        # Step 3: Build hierarchy tree (FR-3.1)
        hierarchy = _hierarchy.build_hierarchy(course.name, course_id, classified_pages)

        # Step 4: Persist to database
        await _course_repo.save_modules(course_id, hierarchy.modules)
        for module in hierarchy.modules:
            await _course_repo.save_pages_with_module(
                course_id, module.id, module.pages,
            )
        if hierarchy.unclassified_pages:
            await _course_repo.save_pages(course_id, hierarchy.unclassified_pages)

        # Update counts
        total_pages = sum(len(m.pages) for m in hierarchy.modules) + len(hierarchy.unclassified_pages)
        await _course_repo.update_course_counts(
            course_id,
            module_count=len(hierarchy.modules),
            page_count=total_pages,
        )
        await _course_repo.update_course_status(course_id, CourseStatus.DISCOVERED)

        return hierarchy

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Discovery failed for course %s: %s", course_id, e, exc_info=True)
        await _course_repo.update_course_status(course_id, CourseStatus.FAILED)
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")


# ── GET /api/courses/{id}/structure ─────────────────────

@router.get("/{course_id}/structure", response_model=CourseHierarchy)
async def get_course_structure(course_id: str):
    """Get the discovered course hierarchy."""
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    modules = await _course_repo.get_modules(course_id)
    unclassified = await _course_repo.get_unclassified_pages(course_id)

    return CourseHierarchy(
        course=course.name,
        course_id=course_id,
        modules=modules,
        unclassified_pages=unclassified,
    )


# ── POST /api/courses/{id}/ingest ──────────────────────

@router.post("/{course_id}/ingest", response_model=IngestionJobResponse)
async def ingest_course(course_id: str, request: IngestRequest, background_tasks: BackgroundTasks):
    """Begin scraping selected pages.

    Starts ingestion as a background task and returns the job immediately.
    """
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    ingestion = _get_ingestion()

    # Create job first for immediate response
    job = await _course_repo.create_job(course_id)

    # Run ingestion in background
    background_tasks.add_task(
        _run_ingestion_background,
        ingestion, course_id, request.page_ids, job.job_id,
    )

    return job


async def _run_ingestion_background(
    ingestion: IngestionService,
    course_id: str,
    page_ids: list[str],
    job_id: str,
):
    """Background task for ingestion."""
    try:
        await ingestion.start_ingestion(course_id, page_ids)
    except Exception as e:
        logger.error("Background ingestion failed: %s", e, exc_info=True)
        await _course_repo.update_job(
            job_id,
            current_stage="failed",
            error=str(e),
        )


# ── GET /api/courses/{id}/progress ──────────────────────

@router.get("/{course_id}/progress", response_model=IngestionJobResponse | None)
async def get_progress(course_id: str):
    """Poll job status for live progress (FR-18.2, AP6)."""
    job = await _course_repo.get_latest_job(course_id)
    if not job:
        raise HTTPException(status_code=404, detail="No ingestion job found for this course")
    return job


# ── POST /api/courses/{id}/process ──────────────────────

@router.post("/{course_id}/process")
async def process_course(course_id: str, background_tasks: BackgroundTasks):
    """Run AI structuring on scraped content."""
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    processing = _get_processing()

    # Run in background
    background_tasks.add_task(processing.process_course, course_id)

    return {"message": "Processing started", "course_id": course_id}


# ── POST /api/courses/{id}/export ───────────────────────

@router.post("/{course_id}/export")
async def export_course(course_id: str):
    """Generate NotebookLM export files."""
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    export_svc = _get_export()
    result = await export_svc.generate_exports(course_id)
    return result


# ── GET /api/courses/{id}/files ─────────────────────────

@router.get("/{course_id}/files", response_model=ExportListResponse)
async def list_files(course_id: str):
    """List/download generated export files."""
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    files_data = _storage.list_exports(course_id)
    files = []
    for f in files_data:
        filename = f["filename"]
        # Determine file type from naming convention
        if "source" in filename:
            file_type = "source"
        elif "knowledge" in filename:
            file_type = "knowledge"
        elif "overview" in filename:
            file_type = "overview"
        elif "quiz" in filename:
            file_type = "quiz"
        elif "glossary" in filename:
            file_type = "glossary"
        elif "sources" in filename:
            file_type = "sources"
        elif "assignment" in filename:
            file_type = "assignment"
        else:
            file_type = "other"

        files.append(ExportFile(
            filename=filename,
            file_type=file_type,
            size_bytes=f["size_bytes"],
            created_at="",  # Could be added from file metadata
        ))

    return ExportListResponse(course_id=course_id, files=files)


# ── GET /api/courses/{id}/files/{filename} ──────────────

@router.get("/{course_id}/files/{filename}")
async def download_file(course_id: str, filename: str):
    """Download a specific export file."""
    # Sanitize filename (FR-20.7)
    safe_filename = Path(filename).name
    if safe_filename != filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = _storage.get_export_path(course_id, safe_filename)
    if not path:
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=str(path),
        filename=safe_filename,
        media_type="text/markdown",
    )

@router.get("/{course_id}/download-zip")
async def download_zip(course_id: str):
    """Download all export files as a single ZIP archive."""
    course = await _course_repo.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # We need the exports directory
    from app.core.config import EXPORTS_DIR
    import shutil
    import tempfile
    import os
    from fastapi.background import BackgroundTask

    course_dir = EXPORTS_DIR / course_id
    if not course_dir.exists() or not any(course_dir.iterdir()):
        raise HTTPException(status_code=404, detail="No export files found for this course")

    # Create a temporary zip file
    fd, temp_zip_path = tempfile.mkstemp(suffix=".zip")
    os.close(fd)

    # make_archive appends .zip to the base_name, so we strip .zip from temp_zip_path
    base_name = temp_zip_path[:-4]
    
    shutil.make_archive(base_name, 'zip', root_dir=str(course_dir))

    def cleanup():
        try:
            os.remove(temp_zip_path)
        except Exception as e:
            logger.error("Failed to delete temp zip %s: %s", temp_zip_path, e)

    return FileResponse(
        path=temp_zip_path,
        filename=f"CourseSync_{course_id[:8]}_Exports.zip",
        media_type="application/zip",
        background=BackgroundTask(cleanup),
    )
