"""
CourseSync — Processing Service (Phase 9)

Orchestrates AI structuring of scraped content.
Uses LLMProvider.structure() only (FR-6.3).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from app.core.exceptions import LLMError
from app.schemas.course import (
    ContentType, CourseStatus, JobStage, PageStatus,
)
from app.schemas.structured import StructuredContent, ClassificationResult
from app.services.llm.provider import LLMProvider
from app.services.storage_service import StorageService
from app.repositories.course_repository import CourseRepository
from app.repositories.content_repository import ContentRepository

logger = logging.getLogger(__name__)


class ProcessingService:
    """Orchestrates AI structuring on scraped content."""

    def __init__(
        self,
        llm: LLMProvider,
        storage: StorageService,
        course_repo: CourseRepository,
        content_repo: ContentRepository,
    ):
        self.llm = llm
        self.storage = storage
        self.course_repo = course_repo
        self.content_repo = content_repo

    async def process_course(self, course_id: str) -> dict:
        """Run AI structuring on all scraped content for a course.

        Returns summary stats: {processed: int, failed: int, structured: list}
        """
        course = await self.course_repo.get_course(course_id)
        if not course:
            return {"processed": 0, "failed": 0, "error": "Course not found"}

        await self.course_repo.update_course_status(course_id, CourseStatus.PROCESSING)

        # Get all scraped content for this course
        scraped_items = await self.content_repo.get_content_by_course(course_id)
        if not scraped_items:
            return {"processed": 0, "failed": 0, "error": "No scraped content found"}

        # Get modules for context
        modules = await self.course_repo.get_modules(course_id)
        module_map = {}
        for m in modules:
            for p in m.pages:
                module_map[p.id] = m.title

        # Update job if one exists
        job = await self.course_repo.get_latest_job(course_id)
        if job:
            await self.course_repo.update_job(job.job_id, current_stage=JobStage.PROCESSING)

        import asyncio
        semaphore = asyncio.Semaphore(10)  # Limit concurrent LLM calls
        db_lock = asyncio.Lock()

        processed = 0
        failed = 0
        structured_results: list[StructuredContent] = []

        async def process_item(item):
            nonlocal processed, failed
            page_id = item["page_id"]
            markdown = item.get("markdown", "")

            if not markdown:
                async with db_lock:
                    failed += 1
                return

            try:
                module_name = module_map.get(page_id, "Unknown Module")
                pages = await self.course_repo.get_pages_by_ids([page_id])
                page = pages[0] if pages else None
                title = page.title if page else "Unknown"
                url = page.url if page else item.get("url", "")
                content_type = page.content_type if page else ContentType.OTHER

                context = {
                    "course_name": course.name,
                    "module_name": module_name,
                    "title": title,
                    "url": url,
                    "content_type": content_type.value,
                }

                # Run AI structuring concurrently but limited by semaphore
                async with semaphore:
                    structured = await self.llm.structure(markdown, context)
                structured.source_url = url

                content_json = structured.model_dump_json()

                # Synchronize DB writes to prevent SQLite locks
                async with db_lock:
                    await self.content_repo.save_structured_content(
                        page_id=page_id,
                        course_id=course_id,
                        content_json=content_json,
                    )
                    self.storage.save_processed(course_id, page_id, content_json)
                    structured_results.append(structured)
                    processed += 1

                    if page:
                        await self.course_repo.update_page_status(page_id, PageStatus.PROCESSED)
                    if job:
                        await self.course_repo.update_job(
                            job.job_id, pages_processed=processed,
                        )

            except Exception as e:
                logger.error("Processing failed for page %s: %s", page_id, e, exc_info=True)
                async with db_lock:
                    failed += 1
                    if page:
                        await self.course_repo.update_page_status(page_id, PageStatus.FAILED)

        # Execute all items concurrently
        await asyncio.gather(*(process_item(item) for item in scraped_items))

        # Update course status
        final_status = CourseStatus.PROCESSED if processed > 0 else CourseStatus.FAILED
        await self.course_repo.update_course_status(course_id, final_status)

        # Update job status
        if job:
            await self.course_repo.update_job(
                job.job_id,
                current_stage="complete" if processed > 0 else "failed",
                error="All pages failed processing" if processed == 0 else None,
            )

        logger.info("Finished processing course %s. Success: %d, Failed: %d", course_id, processed, failed)

        return {
            "processed": processed,
            "failed": failed,
            "total": len(scraped_items),
        }

    async def classify_ambiguous(
        self,
        content: str,
        title: str,
        url: str,
    ) -> ClassificationResult:
        """LLM fallback for ambiguous content types (FR-5.3)."""
        try:
            return await self.llm.classify(
                content,
                {"title": title, "url": url},
            )
        except Exception as e:
            logger.error("LLM classification failed: %s", e)
            return ClassificationResult(
                content_type=ContentType.OTHER,
                confidence=0.0,
                reasoning=f"LLM classification failed: {e}",
            )
