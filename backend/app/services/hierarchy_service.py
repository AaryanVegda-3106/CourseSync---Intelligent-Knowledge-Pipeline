"""
CourseSync — Hierarchy Service (Phase 4)

Organizes classified pages into Course → Modules → Pages tree (FR-3.1).
Structure is stored independently of raw page content (FR-3.2).
"""

from __future__ import annotations

import re
import uuid
import logging
from urllib.parse import urlparse
from collections import defaultdict

from app.schemas.course import ContentType, PageInfo, ModuleInfo, CourseHierarchy

logger = logging.getLogger(__name__)


class HierarchyService:
    """Builds and manages course hierarchy trees."""

    def build_hierarchy(
        self,
        course_name: str,
        course_id: str,
        pages: list[PageInfo],
    ) -> CourseHierarchy:
        """Organize classified pages into a Course → Modules → Pages tree.

        Grouping strategy:
        1. Pages with content_type == MODULE become module containers.
        2. Other pages are grouped by detecting module-like URL path segments.
        3. Remaining ungrouped pages go into unclassified_pages.
        """
        # Separate module-type pages from content pages
        module_pages: list[PageInfo] = []
        content_pages: list[PageInfo] = []

        for page in pages:
            if page.content_type == ContentType.MODULE:
                module_pages.append(page)
            else:
                content_pages.append(page)

        # Strategy 1: If we found explicit module pages, use them as containers
        if module_pages:
            modules = self._build_from_module_pages(module_pages, content_pages)
        else:
            # Strategy 2: Detect modules from URL path structure
            modules = self._detect_modules_from_paths(content_pages)

        # If no modules detected, create a single "Main Content" module
        if not modules and content_pages:
            modules = [
                ModuleInfo(
                    id=str(uuid.uuid4()),
                    title="Main Content",
                    order_index=0,
                    pages=content_pages,
                )
            ]

        # Collect pages that didn't fit into any module
        assigned_ids = set()
        for m in modules:
            for p in m.pages:
                assigned_ids.add(p.id)

        unclassified = [p for p in pages if p.id not in assigned_ids]

        return CourseHierarchy(
            course=course_name,
            course_id=course_id,
            modules=modules,
            unclassified_pages=unclassified,
        )

    def _build_from_module_pages(
        self,
        module_pages: list[PageInfo],
        content_pages: list[PageInfo],
    ) -> list[ModuleInfo]:
        """Build modules from explicit MODULE-type pages and assign content to them."""
        modules: list[ModuleInfo] = []

        # Sort modules by URL path or title to get ordering
        sorted_modules = sorted(module_pages, key=lambda p: (p.url, p.title or ""))

        for idx, mod_page in enumerate(sorted_modules):
            mod_url_parsed = urlparse(mod_page.url)
            mod_path = mod_url_parsed.path.rstrip("/")

            # Find content pages that are children of this module URL
            child_pages = []
            for cp in content_pages:
                cp_parsed = urlparse(cp.url)
                cp_path = cp_parsed.path.rstrip("/")
                if cp_path.startswith(mod_path + "/") or cp_path == mod_path:
                    child_pages.append(cp)

            modules.append(ModuleInfo(
                id=mod_page.id,
                title=mod_page.title or f"Module {idx + 1}",
                order_index=idx,
                pages=child_pages,
            ))

        return modules

    def _detect_modules_from_paths(
        self,
        pages: list[PageInfo],
    ) -> list[ModuleInfo]:
        """Detect module groupings from URL path segments.

        Looks for common path prefixes that suggest module boundaries,
        e.g., /course/module-1/lecture-1 and /course/module-1/quiz
        would group under 'module-1'.
        """
        if not pages:
            return []

        # Group by first divergent path segment
        groups: dict[str, list[PageInfo]] = defaultdict(list)

        for page in pages:
            parsed = urlparse(page.url)
            segments = [s for s in parsed.path.strip("/").split("/") if s]

            if len(segments) >= 2:
                # Use the second-to-last grouping segment as module key
                group_key = segments[-2] if len(segments) >= 2 else segments[0]
                groups[group_key].append(page)
            else:
                groups["_root"].append(page)

        # Convert groups to modules
        modules: list[ModuleInfo] = []
        for idx, (key, group_pages) in enumerate(sorted(groups.items())):
            if key == "_root" and len(groups) > 1:
                continue  # Root pages go to unclassified

            title = self._humanize_segment(key)
            modules.append(ModuleInfo(
                id=str(uuid.uuid4()),
                title=title,
                order_index=idx,
                pages=group_pages,
            ))

        return modules

    @staticmethod
    def _humanize_segment(segment: str) -> str:
        """Convert a URL path segment into a human-readable module title."""
        # Remove common prefixes/suffixes
        segment = re.sub(r"^(module|unit|week|topic|section)[-_]?", "", segment, flags=re.I)
        segment = re.sub(r"[-_]+", " ", segment)

        # If it's just a number, prefix with "Module"
        if segment.strip().isdigit():
            return f"Module {segment.strip()}"

        return segment.strip().title() or "Unnamed Module"
