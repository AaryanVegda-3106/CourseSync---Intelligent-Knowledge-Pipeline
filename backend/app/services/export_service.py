"""
CourseSync — Export Service (Phase 10)

Generates NotebookLM-ready files as the two-layer output (FR-8, FR-9).

Source Layer:  module-XX-source.md  — cleaned original content
Knowledge Layer: module-XX-knowledge.md — AI-structured summaries/concepts

Also generates: course-overview.md, quiz-bank.md, assignments.md,
glossary.md, sources.md (FR-9.2).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from app.core.exceptions import ExportError
from app.schemas.course import CourseStatus, ContentType
from app.schemas.structured import StructuredContent
from app.services.storage_service import StorageService
from app.repositories.course_repository import CourseRepository
from app.repositories.content_repository import ContentRepository

logger = logging.getLogger(__name__)


class ExportService:
    """Generates NotebookLM-ready export files."""

    def __init__(
        self,
        storage: StorageService,
        course_repo: CourseRepository,
        content_repo: ContentRepository,
    ):
        self.storage = storage
        self.course_repo = course_repo
        self.content_repo = content_repo

    async def generate_exports(self, course_id: str) -> dict:
        """Generate all NotebookLM-ready files for a course.

        Returns: {files_generated: int, filenames: list[str]}
        """
        course = await self.course_repo.get_course(course_id)
        if not course:
            raise ExportError("Course not found")

        await self.course_repo.update_course_status(course_id, CourseStatus.EXPORTING)

        modules = await self.course_repo.get_modules(course_id)
        scraped_items = await self.content_repo.get_content_by_course(course_id)
        structured_items = await self.content_repo.get_structured_by_course(course_id)

        # Build lookup maps
        scraped_map: dict[str, dict] = {}
        for item in scraped_items:
            scraped_map[item["page_id"]] = item

        structured_map: dict[str, StructuredContent] = {}
        for item in structured_items:
            try:
                data = json.loads(item["content_json"])
                structured_map[item["page_id"]] = StructuredContent(**data)
            except Exception as e:
                logger.warning("Failed to parse structured content: %s", e)

        filenames: list[str] = []

        # 1. Course Overview (FR-9.2)
        overview = self._generate_course_overview(course, modules, structured_map)
        self.storage.save_export(course_id, "course-overview.md", overview)
        filenames.append("course-overview.md")

        # 2. Module files — Source + Knowledge layers (FR-8.1, FR-8.2)
        for idx, module in enumerate(modules, 1):
            # Source layer (FR-8.1)
            source_md = self._generate_source_layer(module, scraped_map, course)
            source_filename = f"module-{idx:02d}-source.md"
            self.storage.save_export(course_id, source_filename, source_md)
            filenames.append(source_filename)

            # Knowledge layer (FR-8.2)
            knowledge_md = self._generate_knowledge_layer(module, structured_map, course)
            knowledge_filename = f"module-{idx:02d}-knowledge.md"
            self.storage.save_export(course_id, knowledge_filename, knowledge_md)
            filenames.append(knowledge_filename)

        # 3. Quiz Bank (FR-9.2)
        quiz_md = self._generate_quiz_bank(modules, scraped_map, structured_map)
        self.storage.save_export(course_id, "quiz-bank.md", quiz_md)
        filenames.append("quiz-bank.md")

        # 4. Assignments
        assignments_md = self._generate_assignments(modules, scraped_map, structured_map)
        self.storage.save_export(course_id, "assignments.md", assignments_md)
        filenames.append("assignments.md")

        # 5. Glossary (FR-9.2)
        glossary_md = self._generate_glossary(structured_map)
        self.storage.save_export(course_id, "glossary.md", glossary_md)
        filenames.append("glossary.md")

        # 6. Sources (FR-9.2)
        sources_md = self._generate_sources(modules, scraped_map)
        self.storage.save_export(course_id, "sources.md", sources_md)
        filenames.append("sources.md")

        # Update status
        await self.course_repo.update_course_status(course_id, CourseStatus.EXPORTED)

        # Update job
        job = await self.course_repo.get_latest_job(course_id)
        if job:
            await self.course_repo.update_job(
                job.job_id,
                files_generated=len(filenames),
                current_stage="complete",
                completed_at=datetime.now(timezone.utc).isoformat(),
            )

        logger.info("Generated %d export files for course %s", len(filenames), course_id)
        return {"files_generated": len(filenames), "filenames": filenames}

    # ── Course Overview ──────────────────────────────────

    def _generate_course_overview(self, course, modules, structured_map) -> str:
        lines = [
            f"# {course.name}",
            "",
            f"Course URL: {course.url}",
            f"Total Modules: {len(modules)}",
            "",
            "---",
            "",
            "## Course Structure",
            "",
        ]

        for idx, module in enumerate(modules, 1):
            lines.append(f"### Module {idx}: {module.title}")
            lines.append("")
            for page in module.pages:
                type_badge = f"[{page.content_type.value}]" if page.content_type != ContentType.OTHER else ""
                lines.append(f"- {page.title or 'Untitled'} {type_badge}")
            lines.append("")

        # Add summaries from structured content
        summaries = [s for s in structured_map.values() if s.summary]
        if summaries:
            lines.extend(["## Course Summary", ""])
            for s in summaries[:5]:  # Top 5 summaries
                lines.append(f"**{s.title}**: {s.summary}")
                lines.append("")

        return "\n".join(lines)

    # ── Source Layer (FR-8.1) ────────────────────────────

    def _generate_source_layer(self, module, scraped_map, course) -> str:
        """module-XX-source.md — cleaned original content as close to source as possible."""
        lines = [
            f"# {module.title}",
            "",
            f"Course: {course.name}",
            "",
            "Source URLs:",
        ]

        for page in module.pages:
            lines.append(f"- {page.url}")
        lines.extend(["", "---", ""])

        for page in module.pages:
            scraped = scraped_map.get(page.id)
            if not scraped:
                continue

            lines.append(f"## {page.title or 'Untitled'}")
            lines.append("")
            lines.append(f"*Source: {page.url}*")
            lines.append(f"*Type: {page.content_type.value}*")
            lines.append("")

            markdown = scraped.get("markdown", "")
            if markdown:
                lines.append(markdown)
            lines.extend(["", "---", ""])

        return "\n".join(lines)

    # ── Knowledge Layer (FR-8.2) ─────────────────────────

    def _generate_knowledge_layer(self, module, structured_map, course) -> str:
        """module-XX-knowledge.md — AI-structured summaries/concepts/definitions.

        Template per PRD §9.4.
        """
        lines = [
            f"# {module.title}",
            "",
            f"Course: {course.name}",
            "",
            "Source URLs:",
        ]

        for page in module.pages:
            lines.append(f"- {page.url}")
        lines.extend(["", "---", ""])

        # Collect all structured content for this module
        module_structured: list[StructuredContent] = []
        for page in module.pages:
            s = structured_map.get(page.id)
            if s:
                module_structured.append(s)

        if not module_structured:
            lines.append("*No AI-structured content available for this module.*")
            return "\n".join(lines)

        # Overview / summaries
        lines.append("## Overview")
        lines.append("")
        for s in module_structured:
            if s.summary:
                lines.append(f"{s.summary}")
                lines.append("")

        # Learning Objectives
        all_objectives = []
        for s in module_structured:
            all_objectives.extend(s.learning_objectives)
        if all_objectives:
            lines.append("## Learning Objectives")
            lines.append("")
            for obj in all_objectives:
                lines.append(f"- {obj}")
            lines.append("")

        # Content per lecture/page
        for s in module_structured:
            lines.append(f"## {s.title}")
            lines.append("")
            if s.summary:
                lines.append(s.summary)
                lines.append("")

        # Key Concepts
        all_concepts = []
        for s in module_structured:
            all_concepts.extend(s.key_concepts)
        if all_concepts:
            lines.append("## Key Concepts")
            lines.append("")
            for concept in sorted(set(all_concepts)):
                lines.append(f"- **{concept}**")
            lines.append("")

        # Definitions
        all_definitions = []
        for s in module_structured:
            all_definitions.extend(s.definitions)
        if all_definitions:
            lines.append("## Definitions")
            lines.append("")
            for d in all_definitions:
                term = d.get("term", "")
                defn = d.get("definition", "")
                if term and defn:
                    lines.append(f"- **{term}**: {defn}")
            lines.append("")

        # Important Formulas
        all_formulas = []
        for s in module_structured:
            all_formulas.extend(s.important_formulas)
        if all_formulas:
            lines.append("## Important Formulas")
            lines.append("")
            for f in all_formulas:
                lines.append(f"- {f}")
            lines.append("")

        # Quiz Topics
        all_quiz = []
        for s in module_structured:
            all_quiz.extend(s.quiz_topics)
        if all_quiz:
            lines.append("## Quiz Topics")
            lines.append("")
            for t in sorted(set(all_quiz)):
                lines.append(f"- {t}")
            lines.append("")

        # Module Summary
        lines.append("## Module Summary")
        lines.append("")
        for s in module_structured:
            if s.summary:
                lines.append(f"- **{s.title}**: {s.summary}")
        lines.append("")

        return "\n".join(lines)

    # ── Quiz Bank ────────────────────────────────────────

    def _generate_quiz_bank(self, modules, scraped_map, structured_map) -> str:
        lines = ["# Quiz Bank", "", "---", ""]

        for module in modules:
            quiz_pages = [p for p in module.pages if p.content_type == ContentType.QUIZ]
            if not quiz_pages:
                continue

            lines.append(f"## {module.title}")
            lines.append("")

            for page in quiz_pages:
                scraped = scraped_map.get(page.id)
                if scraped and scraped.get("markdown"):
                    lines.append(f"### {page.title or 'Quiz'}")
                    lines.append(f"*Source: {page.url}*")
                    lines.append("")
                    lines.append(scraped["markdown"])
                    lines.extend(["", "---", ""])

        if len(lines) <= 4:
            lines.append("*No quiz content extracted.*")

        return "\n".join(lines)

    # ── Assignments ──────────────────────────────────────

    def _generate_assignments(self, modules, scraped_map, structured_map) -> str:
        lines = ["# Assignments", "", "---", ""]

        for module in modules:
            assignment_pages = [
                p for p in module.pages
                if p.content_type in (ContentType.ASSIGNMENT, ContentType.PROJECT)
            ]
            if not assignment_pages:
                continue

            lines.append(f"## {module.title}")
            lines.append("")

            for page in assignment_pages:
                scraped = scraped_map.get(page.id)
                if scraped and scraped.get("markdown"):
                    lines.append(f"### {page.title or 'Assignment'}")
                    lines.append(f"*Source: {page.url}*")
                    lines.append("")
                    lines.append(scraped["markdown"])
                    lines.extend(["", "---", ""])

        if len(lines) <= 4:
            lines.append("*No assignment content extracted.*")

        return "\n".join(lines)

    # ── Glossary ─────────────────────────────────────────

    def _generate_glossary(self, structured_map) -> str:
        lines = ["# Glossary", "", "---", ""]

        all_definitions: list[dict] = []
        for s in structured_map.values():
            all_definitions.extend(s.definitions)

        if not all_definitions:
            lines.append("*No definitions extracted from course content.*")
            return "\n".join(lines)

        # Deduplicate by term
        seen = set()
        for d in sorted(all_definitions, key=lambda x: x.get("term", "").lower()):
            term = d.get("term", "")
            defn = d.get("definition", "")
            if term and term.lower() not in seen:
                seen.add(term.lower())
                lines.append(f"**{term}**")
                lines.append(f": {defn}")
                lines.append("")

        return "\n".join(lines)

    # ── Sources ──────────────────────────────────────────

    def _generate_sources(self, modules, scraped_map) -> str:
        lines = ["# Sources", "", "All URLs referenced in this course extraction:", "", "---", ""]

        for module in modules:
            lines.append(f"## {module.title}")
            lines.append("")
            for page in module.pages:
                scraped = scraped_map.get(page.id)
                scraped_at = scraped.get("retrieved_at", "N/A") if scraped else "N/A"
                lines.append(
                    f"- [{page.title or page.url}]({page.url}) "
                    f"— *{page.content_type.value}* — Retrieved: {scraped_at}"
                )
            lines.append("")

        return "\n".join(lines)
