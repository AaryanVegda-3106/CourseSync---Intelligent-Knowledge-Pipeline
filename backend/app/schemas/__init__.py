"""
CourseSync — Schemas Package
"""

from app.schemas.course import (
    ContentType,
    CourseStatus,
    JobStage,
    PageStatus,
    CourseCreate,
    CourseResponse,
    CourseListResponse,
    PageInfo,
    ModuleInfo,
    CourseHierarchy,
    IngestionJobResponse,
    IngestRequest,
    ExportFile,
    ExportListResponse,
)
from app.schemas.firecrawl import (
    DiscoveredURL,
    MapResult,
    ScrapeResult,
    CrawlResult,
)
from app.schemas.structured import (
    ClassificationResult,
    StructuredContent,
    QuizQuestion,
)
from app.schemas.errors import (
    ErrorResponse,
    ValidationErrorResponse,
)
