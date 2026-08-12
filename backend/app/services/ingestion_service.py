"""
CourseSync — Ingestion Service (Phase 5)

Orchestrates scraping of selected pages with job tracking.
A single failed page is recorded and skipped — never aborts the job (FR-19.2).
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timezone

from app.core.exceptions import IngestionError
from app.schemas.course import (
    PageInfo, PageStatus, IngestionJobResponse, JobStage, CourseStatus,
)
from app.services.firecrawl_service import FirecrawlService
from app.services.storage_service import StorageService
from app.repositories.course_repository import CourseRepository
from app.repositories.content_repository import ContentRepository

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrates page scraping with progress tracking."""

    def __init__(
        self,
        firecrawl: FirecrawlService,
        storage: StorageService,
        course_repo: CourseRepository,
        content_repo: ContentRepository,
    ):
        self.firecrawl = firecrawl
        self.storage = storage
        self.course_repo = course_repo
        self.content_repo = content_repo

    async def start_ingestion(
        self,
        course_id: str,
        page_ids: list[str],
    ) -> IngestionJobResponse:
        """Create a job and scrape all selected pages."""
        # Create job
        job = await self.course_repo.create_job(course_id)
        job_id = job.job_id

        # Get pages to scrape
        pages = await self.course_repo.get_pages_by_ids(page_ids)
        if not pages:
            await self.course_repo.update_job(
                job_id,
                current_stage=JobStage.FAILED,
                error="No pages found for the given IDs",
                completed_at=datetime.now(timezone.utc).isoformat(),
            )
            return await self.course_repo.get_job(job_id)

        # Update job with discovery count
        await self.course_repo.update_job(
            job_id,
            current_stage=JobStage.SCRAPING,
            pages_discovered=len(pages),
        )
        await self.course_repo.update_course_status(course_id, CourseStatus.INGESTING)

        # Scrape each page
        scraped = 0
        failed = 0

        for page in pages:
            success = await self._scrape_page(course_id, job_id, page)
            if success:
                scraped += 1
            else:
                failed += 1

            # Update progress
            await self.course_repo.update_job(
                job_id,
                pages_scraped=scraped,
                pages_failed=failed,
            )

        # Complete job
        final_stage = JobStage.COMPLETE if scraped > 0 else JobStage.FAILED
        await self.course_repo.update_job(
            job_id,
            current_stage=final_stage,
            completed_at=datetime.now(timezone.utc).isoformat(),
            error=f"{failed} pages failed" if failed > 0 else None,
        )
        await self.course_repo.update_course_status(
            course_id,
            CourseStatus.INGESTED if scraped > 0 else CourseStatus.FAILED,
        )
        await self.course_repo.update_last_synced(course_id)

        return await self.course_repo.get_job(job_id)

    async def _scrape_page(
        self,
        course_id: str,
        job_id: str,
        page: PageInfo,
    ) -> bool:
        """Scrape one page. Returns True on success, False on failure.

        A failure is recorded and skipped — never aborts the job (FR-19.2).
        """
        try:
            # Update page status
            await self.course_repo.update_page_status(page.id, PageStatus.SCRAPING)

            # Check cache first (FR-15.2)
            cached = await self.content_repo.get_cached(page.url)
            if cached:
                logger.info("Using cached content for %s", page.url)
                await self.course_repo.update_page_status(page.id, PageStatus.SCRAPED)
                return True

            # Scrape via Firecrawl
            result = await self.firecrawl.scrape_page(page.url, course_id=course_id)

            if not result.success or not result.markdown:
                logger.warning("Scrape failed for %s: %s", page.url, result.error)
                await self.course_repo.update_page_status(page.id, PageStatus.FAILED)
                return False

            # Compute content hash for deduplication (FR-14.1)
            content_hash = hashlib.sha256(result.markdown.encode()).hexdigest()

            # Check for duplicate
            if await self.content_repo.is_duplicate(page.url, content_hash):
                logger.info("Duplicate content for %s, skipping", page.url)
                await self.course_repo.update_page_status(page.id, PageStatus.SCRAPED)
                return True

            # Save to database
            await self.content_repo.save_scraped_content(
                page_id=page.id,
                course_id=course_id,
                url=page.url,
                content_hash=content_hash,
                markdown=result.markdown,
                metadata=result.metadata,
            )

            # Save to filesystem
            self.storage.save_raw_markdown(
                course_id=course_id,
                page_id=page.id,
                content=result.markdown,
                metadata={
                    "url": page.url,
                    "title": result.title or page.title,
                    "content_type": page.content_type.value,
                    "content_hash": content_hash,
                    "scraped_at": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Update page
            await self.course_repo.update_page_status(page.id, PageStatus.SCRAPED)
            await self.course_repo.update_page_hash(page.id, content_hash)

            return True

        except Exception as e:
            logger.error(
                "Failed to scrape page %s (%s): %s",
                page.id, page.url, e, exc_info=True,
            )
            await self.course_repo.update_page_status(page.id, PageStatus.FAILED)
            return False

    async def get_progress(self, course_id: str) -> IngestionJobResponse | None:
        """Return latest job progress for polling (AP6)."""
        return await self.course_repo.get_latest_job(course_id)
