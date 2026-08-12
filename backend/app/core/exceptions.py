"""
CourseSync — Custom Exceptions

Centralized exception hierarchy for clean error propagation
through the service layer up to API error handlers.
"""

from __future__ import annotations


class CourseSyncError(Exception):
    """Base exception for all CourseSync errors."""

    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class FirecrawlError(CourseSyncError):
    """Error originating from the Firecrawl SDK/API."""

    def __init__(self, message: str, url: str | None = None, stage: str | None = None, detail: str | None = None):
        self.url = url
        self.stage = stage
        super().__init__(message, detail)


class DiscoveryError(CourseSyncError):
    """Error during URL discovery or classification."""
    pass


class IngestionError(CourseSyncError):
    """Error during page scraping / ingestion."""
    pass


class LLMError(CourseSyncError):
    """Error from the LLM provider layer."""

    def __init__(self, message: str, provider: str | None = None, detail: str | None = None):
        self.provider = provider
        super().__init__(message, detail)


class ExportError(CourseSyncError):
    """Error during file export generation."""
    pass


class NotFoundError(CourseSyncError):
    """Requested resource not found."""
    pass


class ValidationError(CourseSyncError):
    """Input validation failure."""
    pass
