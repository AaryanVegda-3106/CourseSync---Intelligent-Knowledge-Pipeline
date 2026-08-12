"""
CourseSync — Firecrawl Schemas

Internal normalized models for Firecrawl responses (FR-1.4).
The rest of the app never sees raw Firecrawl SDK objects.
"""

from __future__ import annotations

from pydantic import BaseModel


class DiscoveredURL(BaseModel):
    """A single URL discovered by Firecrawl Map."""
    url: str
    title: str | None = None


class MapResult(BaseModel):
    """Normalized result from FirecrawlService.map_course()."""
    success: bool
    source_url: str
    links: list[DiscoveredURL] = []
    total_found: int = 0
    error: str | None = None


class ScrapeResult(BaseModel):
    """Normalized result from FirecrawlService.scrape_page()."""
    success: bool
    url: str
    markdown: str | None = None
    title: str | None = None
    metadata: dict = {}
    error: str | None = None


class CrawlResult(BaseModel):
    """Normalized result from FirecrawlService.crawl_course()."""
    success: bool
    source_url: str
    pages: list[ScrapeResult] = []
    total_pages: int = 0
    error: str | None = None
