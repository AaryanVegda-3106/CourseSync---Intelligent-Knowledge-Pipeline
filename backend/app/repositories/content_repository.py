"""
CourseSync — Content Repository

Manages scraped content storage and deduplication (FR-14, FR-15).
"""

from __future__ import annotations

import uuid
import json
from datetime import datetime, timezone

from app.core.database import get_db


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ContentRepository:
    """Data-access layer for scraped and structured content."""

    # ── Scraped Content ─────────────────────────────────

    async def save_scraped_content(
        self,
        page_id: str,
        course_id: str,
        url: str,
        content_hash: str,
        markdown: str,
        metadata: dict | None = None,
    ) -> str:
        """Save scraped content. Returns the content ID."""
        content_id = str(uuid.uuid4())
        async with get_db() as db:
            await db.execute(
                """INSERT OR REPLACE INTO scraped_content
                   (id, page_id, course_id, url, content_hash, markdown, metadata_json, retrieved_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    content_id, page_id, course_id, url, content_hash,
                    markdown, json.dumps(metadata or {}), _now(),
                ),
            )
            await db.commit()
        return content_id

    async def get_content_by_page(self, page_id: str) -> dict | None:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM scraped_content WHERE page_id = ?", (page_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return dict(row)

    async def get_content_by_course(self, course_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM scraped_content WHERE course_id = ? ORDER BY retrieved_at",
                (course_id,),
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def is_duplicate(self, url: str, content_hash: str) -> bool:
        """Check if content with this URL + hash already exists (FR-14.1)."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT 1 FROM scraped_content WHERE url = ? AND content_hash = ? LIMIT 1",
                (url, content_hash),
            )
            return await cursor.fetchone() is not None

    async def get_cached(self, url: str) -> dict | None:
        """Get the most recent scrape for a URL if cached (FR-15)."""
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM scraped_content WHERE url = ? ORDER BY retrieved_at DESC LIMIT 1",
                (url,),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return dict(row)

    # ── Structured Content ──────────────────────────────

    async def save_structured_content(
        self,
        page_id: str,
        course_id: str,
        content_json: str,
    ) -> str:
        """Save AI-structured content for a page."""
        content_id = str(uuid.uuid4())
        async with get_db() as db:
            await db.execute(
                """INSERT OR REPLACE INTO structured_content
                   (id, page_id, course_id, content_json, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (content_id, page_id, course_id, content_json, _now()),
            )
            await db.commit()
        return content_id

    async def get_structured_by_course(self, course_id: str) -> list[dict]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM structured_content WHERE course_id = ? ORDER BY created_at",
                (course_id,),
            )
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

    async def get_structured_by_page(self, page_id: str) -> dict | None:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM structured_content WHERE page_id = ?", (page_id,)
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return dict(row)
