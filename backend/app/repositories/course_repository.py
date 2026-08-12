"""
CourseSync — Course Repository

Abstracts all database operations for courses, modules, pages, and jobs.
Repository pattern (AP3): swap SQLite → PostgreSQL here, not in services.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

import aiosqlite

from app.core.database import get_db
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseStatus,
    PageInfo,
    PageStatus,
    ModuleInfo,
    CourseHierarchy,
    IngestionJobResponse,
    JobStage,
    ContentType,
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


class CourseRepository:
    """Data-access layer for courses and related entities."""

    # ── Courses ─────────────────────────────────────────

    async def create_course(self, data: CourseCreate) -> CourseResponse:
        now = _now()
        course_id = _uuid()
        async with get_db() as db:
            await db.execute(
                """INSERT INTO courses (id, name, url, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (course_id, data.name, data.url, CourseStatus.CREATED.value, now, now),
            )
            await db.commit()
        return CourseResponse(
            id=course_id, name=data.name, url=data.url,
            status=CourseStatus.CREATED, created_at=now, updated_at=now,
        )

    async def get_course(self, course_id: str) -> CourseResponse | None:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return self._row_to_course(row)

    async def list_courses(self) -> list[CourseResponse]:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM courses ORDER BY created_at DESC")
            rows = await cursor.fetchall()
            return [self._row_to_course(r) for r in rows]

    async def update_course_status(self, course_id: str, status: CourseStatus) -> None:
        async with get_db() as db:
            await db.execute(
                "UPDATE courses SET status = ?, updated_at = ? WHERE id = ?",
                (status.value, _now(), course_id),
            )
            await db.commit()

    async def delete_course(self, course_id: str) -> bool:
        async with get_db() as db:
            cursor = await db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def update_course_counts(self, course_id: str, module_count: int, page_count: int) -> None:
        async with get_db() as db:
            await db.execute(
                "UPDATE courses SET module_count = ?, page_count = ?, updated_at = ? WHERE id = ?",
                (module_count, page_count, _now(), course_id),
            )
            await db.commit()

    async def update_last_synced(self, course_id: str) -> None:
        now = _now()
        async with get_db() as db:
            await db.execute(
                "UPDATE courses SET last_synced_at = ?, updated_at = ? WHERE id = ?",
                (now, now, course_id),
            )
            await db.commit()

    # ── Modules ─────────────────────────────────────────

    async def save_modules(self, course_id: str, modules: list[ModuleInfo]) -> None:
        now = _now()
        async with get_db() as db:
            # Clear existing modules for this course
            await db.execute("DELETE FROM modules WHERE course_id = ?", (course_id,))
            for m in modules:
                await db.execute(
                    """INSERT INTO modules (id, course_id, title, order_index, created_at)
                       VALUES (?, ?, ?, ?, ?)""",
                    (m.id, course_id, m.title, m.order_index, now),
                )
            await db.commit()

    async def get_modules(self, course_id: str) -> list[ModuleInfo]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM modules WHERE course_id = ? ORDER BY order_index",
                (course_id,),
            )
            rows = await cursor.fetchall()
            modules = []
            for row in rows:
                pages = await self.get_pages_for_module(course_id, row["id"])
                modules.append(ModuleInfo(
                    id=row["id"],
                    title=row["title"],
                    order_index=row["order_index"],
                    pages=pages,
                ))
            return modules

    # ── Pages ───────────────────────────────────────────

    async def save_pages(self, course_id: str, pages: list[PageInfo]) -> None:
        now = _now()
        async with get_db() as db:
            for p in pages:
                await db.execute(
                    """INSERT OR REPLACE INTO pages
                       (id, course_id, module_id, title, url, content_type, status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (p.id, course_id, None, p.title, p.url, p.content_type.value, p.status.value, now),
                )
            await db.commit()

    async def save_pages_with_module(self, course_id: str, module_id: str, pages: list[PageInfo]) -> None:
        now = _now()
        async with get_db() as db:
            for p in pages:
                await db.execute(
                    """INSERT OR REPLACE INTO pages
                       (id, course_id, module_id, title, url, content_type, status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (p.id, course_id, module_id, p.title, p.url, p.content_type.value, p.status.value, now),
                )
            await db.commit()

    async def get_pages_for_module(self, course_id: str, module_id: str) -> list[PageInfo]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM pages WHERE course_id = ? AND module_id = ?",
                (course_id, module_id),
            )
            rows = await cursor.fetchall()
            return [self._row_to_page(r) for r in rows]

    async def get_unclassified_pages(self, course_id: str) -> list[PageInfo]:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM pages WHERE course_id = ? AND module_id IS NULL",
                (course_id,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_page(r) for r in rows]

    async def get_pages_by_ids(self, page_ids: list[str]) -> list[PageInfo]:
        if not page_ids:
            return []
        placeholders = ",".join("?" for _ in page_ids)
        async with get_db() as db:
            cursor = await db.execute(
                f"SELECT * FROM pages WHERE id IN ({placeholders})",
                page_ids,
            )
            rows = await cursor.fetchall()
            return [self._row_to_page(r) for r in rows]

    async def update_page_status(self, page_id: str, status: PageStatus) -> None:
        async with get_db() as db:
            await db.execute(
                "UPDATE pages SET status = ? WHERE id = ?",
                (status.value, page_id),
            )
            await db.commit()

    async def update_page_hash(self, page_id: str, content_hash: str) -> None:
        async with get_db() as db:
            await db.execute(
                "UPDATE pages SET content_hash = ?, scraped_at = ? WHERE id = ?",
                (content_hash, _now(), page_id),
            )
            await db.commit()

    # ── Ingestion Jobs ──────────────────────────────────

    async def create_job(self, course_id: str) -> IngestionJobResponse:
        job_id = _uuid()
        now = _now()
        async with get_db() as db:
            await db.execute(
                """INSERT INTO ingestion_jobs
                   (id, course_id, current_stage, started_at)
                   VALUES (?, ?, ?, ?)""",
                (job_id, course_id, JobStage.MAPPING.value, now),
            )
            await db.commit()
        return IngestionJobResponse(
            job_id=job_id, course_id=course_id,
            current_stage=JobStage.MAPPING, started_at=now,
        )

    async def update_job(self, job_id: str, **kwargs) -> None:
        if not kwargs:
            return
        set_clauses = []
        values = []
        for key, val in kwargs.items():
            if isinstance(val, JobStage):
                val = val.value
            set_clauses.append(f"{key} = ?")
            values.append(val)
        values.append(job_id)
        async with get_db() as db:
            await db.execute(
                f"UPDATE ingestion_jobs SET {', '.join(set_clauses)} WHERE id = ?",
                values,
            )
            await db.commit()

    async def get_job(self, job_id: str) -> IngestionJobResponse | None:
        async with get_db() as db:
            cursor = await db.execute("SELECT * FROM ingestion_jobs WHERE id = ?", (job_id,))
            row = await cursor.fetchone()
            if not row:
                return None
            return self._row_to_job(row)

    async def get_latest_job(self, course_id: str) -> IngestionJobResponse | None:
        async with get_db() as db:
            cursor = await db.execute(
                "SELECT * FROM ingestion_jobs WHERE course_id = ? ORDER BY started_at DESC LIMIT 1",
                (course_id,),
            )
            row = await cursor.fetchone()
            if not row:
                return None
            return self._row_to_job(row)

    # ── Row Converters ──────────────────────────────────

    @staticmethod
    def _row_to_course(row: aiosqlite.Row) -> CourseResponse:
        return CourseResponse(
            id=row["id"],
            name=row["name"],
            url=row["url"],
            status=CourseStatus(row["status"]),
            module_count=row["module_count"],
            page_count=row["page_count"],
            last_synced_at=row["last_synced_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_page(row: aiosqlite.Row) -> PageInfo:
        return PageInfo(
            id=row["id"],
            title=row["title"],
            url=row["url"],
            content_type=ContentType(row["content_type"]),
            status=PageStatus(row["status"]),
        )

    @staticmethod
    def _row_to_job(row: aiosqlite.Row) -> IngestionJobResponse:
        return IngestionJobResponse(
            job_id=row["id"],
            course_id=row["course_id"],
            current_stage=JobStage(row["current_stage"]),
            pages_discovered=row["pages_discovered"],
            pages_scraped=row["pages_scraped"],
            pages_failed=row["pages_failed"],
            pages_processed=row["pages_processed"],
            files_generated=row["files_generated"],
            started_at=row["started_at"],
            completed_at=row["completed_at"],
            error=row["error"],
        )
