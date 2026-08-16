"""
CourseSync — Firecrawl Service (Phase 2)

The SOLE module allowed to import the Firecrawl SDK (AP1 / FR-1.7).
All other modules interact with Firecrawl through this service.
"""

from __future__ import annotations

import asyncio
import json
import hashlib
import logging
from pathlib import Path
from typing import Any

from app.core.config import RAW_DIR
from app.core.exceptions import FirecrawlError
from app.schemas.firecrawl import DiscoveredURL, MapResult, ScrapeResult, CrawlResult

logger = logging.getLogger(__name__)


class FirecrawlService:
    """Encapsulates all Firecrawl SDK interactions."""

    def __init__(self, api_key: str):
        if not api_key:
            raise FirecrawlError("Firecrawl API key is required", stage="init")
        self._api_key = api_key
        self._client = None

    def _get_client(self):
        """Lazy-init the Firecrawl client."""
        if self._client is None:
            try:
                from firecrawl import Firecrawl
                self._client = Firecrawl(api_key=self._api_key)
            except ImportError as e:
                raise FirecrawlError(
                    f"firecrawl-py package not installed or failed to load. Original error: {e}",
                    stage="init",
                )
            except Exception as e:
                raise FirecrawlError(
                    f"Failed to initialize Firecrawl client: {e}",
                    stage="init",
                    detail=str(e),
                )
        return self._client

    # ── Map (FR-2.1) ────────────────────────────────────

    async def map_course(self, url: str, limit: int = 500) -> MapResult:
        """Discover all URLs under a course domain via Firecrawl Map.

        Returns normalized MapResult, never raw SDK response (FR-1.4).
        """
        logger.info("Firecrawl Map: %s (limit=%d)", url, limit)
        try:
            client = self._get_client()
            response = await asyncio.to_thread(
                client.map, url=url, limit=limit
            )

            # Normalize response
            links: list[DiscoveredURL] = []
            raw_links = []

            if isinstance(response, dict):
                raw_links = response.get("links", [])
            elif isinstance(response, list):
                raw_links = response
            elif hasattr(response, "links"):
                raw_links = response.links or []

            for link in raw_links:
                if isinstance(link, str):
                    links.append(DiscoveredURL(url=link))
                elif isinstance(link, dict):
                    links.append(DiscoveredURL(
                        url=link.get("url", link.get("link", "")),
                        title=link.get("title"),
                    ))
                elif hasattr(link, "url"):
                    links.append(DiscoveredURL(url=link.url, title=getattr(link, "title", None)))

            result = MapResult(
                success=True,
                source_url=url,
                links=links,
                total_found=len(links),
            )
            logger.info("Firecrawl Map found %d URLs for %s", len(links), url)
            return result

        except FirecrawlError:
            raise
        except Exception as e:
            logger.error("Firecrawl Map failed for %s: %s", url, e, exc_info=True)
            return MapResult(success=False, source_url=url, error=str(e))

    # ── Scrape (FR-4.1) ─────────────────────────────────

    async def scrape_page(self, url: str, course_id: str | None = None) -> ScrapeResult:
        """Scrape a single page for markdown content.

        Persists raw result to data/raw/ when course_id provided (FR-1.6).
        Preserves original URL, page title, and metadata (FR-1.5).
        """
        logger.info("Firecrawl Scrape: %s", url)
        try:
            client = self._get_client()
            response = await asyncio.to_thread(
                client.scrape, url, formats=["markdown"]
            )

            # Normalize response
            markdown = None
            title = None
            metadata: dict[str, Any] = {}

            if isinstance(response, dict):
                markdown = response.get("markdown", "")
                metadata = response.get("metadata", {})
                title = metadata.get("title") or response.get("title")
            elif hasattr(response, "markdown"):
                markdown = response.markdown or ""
                metadata = getattr(response, "metadata", {}) or {}
                if isinstance(metadata, object) and not isinstance(metadata, dict):
                    metadata = dict(metadata) if hasattr(metadata, "__iter__") else {}
                title = metadata.get("title") if isinstance(metadata, dict) else None

            # Always include source URL in metadata (FR-1.5)
            if isinstance(metadata, dict):
                metadata["source_url"] = url
            else:
                metadata = {"source_url": url}

            result = ScrapeResult(
                success=True,
                url=url,
                markdown=markdown,
                title=title,
                metadata=metadata,
            )

            # Persist raw result (FR-1.6)
            if course_id:
                await self._persist_raw(course_id, url, result)

            logger.info("Firecrawl Scrape success: %s (%d chars)", url, len(markdown or ""))
            return result

        except FirecrawlError:
            raise
        except Exception as e:
            logger.error("Firecrawl Scrape failed for %s: %s", url, e, exc_info=True)
            return ScrapeResult(success=False, url=url, error=str(e))

    # ── Crawl ────────────────────────────────────────────

    async def crawl_course(self, url: str, limit: int = 100) -> CrawlResult:
        """Multi-page crawl with Firecrawl."""
        logger.info("Firecrawl Crawl: %s (limit=%d)", url, limit)
        try:
            client = self._get_client()

            from firecrawl.types import ScrapeOptions
            response = await asyncio.to_thread(
                client.crawl,
                url,
                limit=limit,
                scrape_options=ScrapeOptions(formats=["markdown"]),
            )

            pages: list[ScrapeResult] = []
            raw_data = []

            if isinstance(response, dict):
                raw_data = response.get("data", [])
            elif isinstance(response, list):
                raw_data = response
            elif hasattr(response, "data"):
                raw_data = response.data or []

            for item in raw_data:
                if isinstance(item, dict):
                    pages.append(ScrapeResult(
                        success=True,
                        url=item.get("metadata", {}).get("url", item.get("url", "")),
                        markdown=item.get("markdown", ""),
                        title=item.get("metadata", {}).get("title"),
                        metadata=item.get("metadata", {}),
                    ))
                elif hasattr(item, "markdown"):
                    meta = getattr(item, "metadata", {}) or {}
                    pages.append(ScrapeResult(
                        success=True,
                        url=getattr(meta, "url", getattr(item, "url", "")),
                        markdown=item.markdown or "",
                        title=getattr(meta, "title", None),
                        metadata=meta if isinstance(meta, dict) else {},
                    ))

            return CrawlResult(
                success=True,
                source_url=url,
                pages=pages,
                total_pages=len(pages),
            )

        except Exception as e:
            logger.error("Firecrawl Crawl failed for %s: %s", url, e, exc_info=True)
            return CrawlResult(success=False, source_url=url, error=str(e))

    # ── Internal Helpers ─────────────────────────────────

    async def _persist_raw(self, course_id: str, url: str, result: ScrapeResult) -> None:
        """Save raw scrape result to filesystem (FR-1.6)."""
        try:
            course_dir = RAW_DIR / course_id
            course_dir.mkdir(parents=True, exist_ok=True)
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            filepath = course_dir / f"{url_hash}.json"
            data = result.model_dump()
            await asyncio.to_thread(filepath.write_text, json.dumps(data, indent=2), "utf-8")
        except Exception as e:
            logger.warning("Failed to persist raw result for %s: %s", url, e)
