"""
CourseSync — Course & Hierarchy Schemas

Pydantic models for courses, modules, pages, ingestion jobs,
and the course hierarchy tree (PRD §9.1, §9.5).
"""

from __future__ import annotations

from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


# ── Content Type Enum (PRD §9.2) ────────────────────────────

class ContentType(str, Enum):
    COURSE_OVERVIEW = "course_overview"
    MODULE = "module"
    LECTURE = "lecture"
    READING = "reading"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    ANNOUNCEMENT = "announcement"
    REFERENCE = "reference"
    PDF = "pdf"
    VIDEO = "video"
    OTHER = "other"


# ── Course Status ────────────────────────────────────────────

class CourseStatus(str, Enum):
    CREATED = "created"
    DISCOVERING = "discovering"
    DISCOVERED = "discovered"
    INGESTING = "ingesting"
    INGESTED = "ingested"
    PROCESSING = "processing"
    PROCESSED = "processed"
    EXPORTING = "exporting"
    EXPORTED = "exported"
    FAILED = "failed"


# ── Job Stage (PRD §9.5) ────────────────────────────────────

class JobStage(str, Enum):
    MAPPING = "mapping"
    DISCOVERING = "discovering"
    SCRAPING = "scraping"
    PROCESSING = "processing"
    EXPORTING = "exporting"
    COMPLETE = "complete"
    FAILED = "failed"


# ── Page Status ──────────────────────────────────────────────

class PageStatus(str, Enum):
    DISCOVERED = "discovered"
    SELECTED = "selected"
    SCRAPING = "scraping"
    SCRAPED = "scraped"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    SKIPPED = "skipped"


# ── Request / Response Models ────────────────────────────────

class CourseCreate(BaseModel):
    """POST /api/courses request body."""
    name: str = Field(..., min_length=1, max_length=500, description="Human-readable course name")
    url: str = Field(..., min_length=1, description="Course root URL")


class CourseResponse(BaseModel):
    """Single course in API responses."""
    id: str
    name: str
    url: str
    status: CourseStatus
    module_count: int = 0
    page_count: int = 0
    last_synced_at: str | None = None
    created_at: str
    updated_at: str


class CourseListResponse(BaseModel):
    """GET /api/courses response body."""
    courses: list[CourseResponse]
    total: int


# ── Page / Module Models ────────────────────────────────────

class PageInfo(BaseModel):
    """A single page within the hierarchy."""
    id: str
    title: str | None = None
    url: str
    content_type: ContentType = ContentType.OTHER
    status: PageStatus = PageStatus.DISCOVERED


class ModuleInfo(BaseModel):
    """A module containing pages."""
    id: str
    title: str
    order_index: int = 0
    pages: list[PageInfo] = []


class CourseHierarchy(BaseModel):
    """Full course hierarchy tree (PRD §9.1)."""
    course: str
    course_id: str
    modules: list[ModuleInfo] = []
    unclassified_pages: list[PageInfo] = []


# ── Ingestion Job (PRD §9.5) ────────────────────────────────

class IngestionJobResponse(BaseModel):
    """Job progress response for polling."""
    job_id: str
    course_id: str
    current_stage: JobStage
    pages_discovered: int = 0
    pages_scraped: int = 0
    pages_failed: int = 0
    pages_processed: int = 0
    files_generated: int = 0
    started_at: str
    completed_at: str | None = None
    error: str | None = None


# ── Ingestion Request ───────────────────────────────────────

class IngestRequest(BaseModel):
    """POST /api/courses/{id}/ingest request body."""
    page_ids: list[str] = Field(..., min_length=1, description="IDs of pages to scrape")


# ── Export File ──────────────────────────────────────────────

class ExportFile(BaseModel):
    """A generated export file."""
    filename: str
    file_type: str  # "source" | "knowledge" | "overview" | "quiz" | "glossary" | "sources"
    size_bytes: int
    created_at: str


class ExportListResponse(BaseModel):
    """GET /api/courses/{id}/files response."""
    course_id: str
    files: list[ExportFile]
