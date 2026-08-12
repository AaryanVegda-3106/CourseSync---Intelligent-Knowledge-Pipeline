"""
CourseSync — Discovery Service (Phase 3)

Deterministic URL classification — no LLM used here (FR-2.4).
Classifies discovered URLs by path patterns and title keywords.
"""

from __future__ import annotations

import re
import uuid
import logging
from urllib.parse import urlparse, urljoin

from app.schemas.course import ContentType, PageInfo, PageStatus
from app.schemas.firecrawl import DiscoveredURL

logger = logging.getLogger(__name__)


# ── URL Path Patterns for Classification ──────────────────

_PATH_PATTERNS: list[tuple[re.Pattern, ContentType]] = [
    (re.compile(r"/quiz", re.I), ContentType.QUIZ),
    (re.compile(r"/exam", re.I), ContentType.QUIZ),
    (re.compile(r"/test[/-]", re.I), ContentType.QUIZ),
    (re.compile(r"/assignment", re.I), ContentType.ASSIGNMENT),
    (re.compile(r"/homework", re.I), ContentType.ASSIGNMENT),
    (re.compile(r"/hw[/-]", re.I), ContentType.ASSIGNMENT),
    (re.compile(r"/project", re.I), ContentType.PROJECT),
    (re.compile(r"/lab[/-]", re.I), ContentType.PROJECT),
    (re.compile(r"/lecture", re.I), ContentType.LECTURE),
    (re.compile(r"/lesson", re.I), ContentType.LECTURE),
    (re.compile(r"/slide", re.I), ContentType.LECTURE),
    (re.compile(r"/reading", re.I), ContentType.READING),
    (re.compile(r"/textbook", re.I), ContentType.READING),
    (re.compile(r"/chapter", re.I), ContentType.READING),
    (re.compile(r"/module", re.I), ContentType.MODULE),
    (re.compile(r"/unit[/-]", re.I), ContentType.MODULE),
    (re.compile(r"/week[/-]", re.I), ContentType.MODULE),
    (re.compile(r"/topic[/-]", re.I), ContentType.MODULE),
    (re.compile(r"/syllabus", re.I), ContentType.COURSE_OVERVIEW),
    (re.compile(r"/overview", re.I), ContentType.COURSE_OVERVIEW),
    (re.compile(r"/course[-_]?info", re.I), ContentType.COURSE_OVERVIEW),
    (re.compile(r"/announcement", re.I), ContentType.ANNOUNCEMENT),
    (re.compile(r"/news", re.I), ContentType.ANNOUNCEMENT),
    (re.compile(r"/video", re.I), ContentType.VIDEO),
    (re.compile(r"/media", re.I), ContentType.VIDEO),
    (re.compile(r"/reference", re.I), ContentType.REFERENCE),
    (re.compile(r"/resource", re.I), ContentType.REFERENCE),
    (re.compile(r"/bibliography", re.I), ContentType.REFERENCE),
]

# ── Title Keyword Patterns ─────────────────────────────────

_TITLE_PATTERNS: list[tuple[re.Pattern, ContentType]] = [
    (re.compile(r"\bquiz\b", re.I), ContentType.QUIZ),
    (re.compile(r"\bexam\b", re.I), ContentType.QUIZ),
    (re.compile(r"\bmidterm\b", re.I), ContentType.QUIZ),
    (re.compile(r"\bfinal\s+exam\b", re.I), ContentType.QUIZ),
    (re.compile(r"\bassignment\b", re.I), ContentType.ASSIGNMENT),
    (re.compile(r"\bhomework\b", re.I), ContentType.ASSIGNMENT),
    (re.compile(r"\bproject\b", re.I), ContentType.PROJECT),
    (re.compile(r"\blab\b", re.I), ContentType.PROJECT),
    (re.compile(r"\blecture\b", re.I), ContentType.LECTURE),
    (re.compile(r"\blesson\b", re.I), ContentType.LECTURE),
    (re.compile(r"\breading\b", re.I), ContentType.READING),
    (re.compile(r"\bchapter\b", re.I), ContentType.READING),
    (re.compile(r"\bmodule\b", re.I), ContentType.MODULE),
    (re.compile(r"\bunit\s+\d", re.I), ContentType.MODULE),
    (re.compile(r"\bweek\s+\d", re.I), ContentType.MODULE),
    (re.compile(r"\bsyllabus\b", re.I), ContentType.COURSE_OVERVIEW),
    (re.compile(r"\bcourse\s+overview\b", re.I), ContentType.COURSE_OVERVIEW),
    (re.compile(r"\bannouncement", re.I), ContentType.ANNOUNCEMENT),
]

# ── URLs to always filter out ──────────────────────────────

_IRRELEVANT_PATTERNS: list[re.Pattern] = [
    re.compile(r"/login", re.I),
    re.compile(r"/logout", re.I),
    re.compile(r"/sign[-_]?in", re.I),
    re.compile(r"/sign[-_]?up", re.I),
    re.compile(r"/register", re.I),
    re.compile(r"/password", re.I),
    re.compile(r"/auth", re.I),
    re.compile(r"/oauth", re.I),
    re.compile(r"/sso", re.I),
    re.compile(r"/admin", re.I),
    re.compile(r"/settings", re.I),
    re.compile(r"/profile", re.I),
    re.compile(r"/account", re.I),
    re.compile(r"/cart", re.I),
    re.compile(r"/checkout", re.I),
    re.compile(r"/privacy", re.I),
    re.compile(r"/terms", re.I),
    re.compile(r"/cookie", re.I),
    re.compile(r"/sitemap\.xml", re.I),
    re.compile(r"/robots\.txt", re.I),
    re.compile(r"/favicon", re.I),
    re.compile(r"\.(css|js|woff|woff2|ttf|eot|svg|ico)$", re.I),
    re.compile(r"#"),  # Fragment-only links
    re.compile(r"^mailto:", re.I),
    re.compile(r"^tel:", re.I),
    re.compile(r"^javascript:", re.I),
]

# ── File extensions for PDF detection ──────────────────────

_PDF_PATTERN = re.compile(r"\.(pdf)$", re.I)
_DOC_PATTERN = re.compile(r"\.(docx?|pptx?|xlsx?|csv)$", re.I)


class DiscoveryService:
    """Filters and classifies discovered URLs using deterministic heuristics."""

    def discover(
        self,
        course_url: str,
        mapped_urls: list[DiscoveredURL],
    ) -> list[PageInfo]:
        """Filter mapped URLs to course-relevant candidates and classify them.

        Returns classified PageInfo list ready for user review (FR-2.5).
        """
        course_base = self._get_base_domain(course_url)
        results: list[PageInfo] = []
        seen_urls: set[str] = set()

        for discovered in mapped_urls:
            url = discovered.url.strip()

            # Deduplicate
            canonical = self._canonicalize(url)
            if canonical in seen_urls:
                continue
            seen_urls.add(canonical)

            # Filter irrelevant
            if not self._is_course_relevant(url, course_base):
                continue

            # Classify
            content_type = self._classify_url(url, discovered.title)

            results.append(PageInfo(
                id=str(uuid.uuid4()),
                title=discovered.title or self._title_from_url(url),
                url=url,
                content_type=content_type,
                status=PageStatus.DISCOVERED,
            ))

        logger.info(
            "Discovery: %d/%d URLs classified as course-relevant",
            len(results), len(mapped_urls),
        )
        return results

    def _classify_url(self, url: str, title: str | None) -> ContentType:
        """Deterministic classification via URL path + title keywords (FR-2.3)."""
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Check for file types
        if _PDF_PATTERN.search(path):
            return ContentType.PDF
        if _DOC_PATTERN.search(path):
            return ContentType.REFERENCE

        # Match URL path patterns
        for pattern, content_type in _PATH_PATTERNS:
            if pattern.search(path):
                return content_type

        # Match title patterns
        if title:
            for pattern, content_type in _TITLE_PATTERNS:
                if pattern.search(title):
                    return content_type

        return ContentType.OTHER

    def _is_course_relevant(self, url: str, course_base: str) -> bool:
        """Filter out navigation, auth, external, and irrelevant URLs (FR-2.2)."""
        if not url or not url.startswith(("http://", "https://")):
            return False

        # Filter irrelevant patterns
        for pattern in _IRRELEVANT_PATTERNS:
            if pattern.search(url):
                return False

        # Must be same domain or subdomain
        url_base = self._get_base_domain(url)
        if course_base and url_base != course_base:
            return False

        return True

    @staticmethod
    def _get_base_domain(url: str) -> str:
        """Extract base domain for same-site checks (FR-20.3)."""
        try:
            parsed = urlparse(url)
            host = parsed.hostname or ""
            # Strip 'www.' prefix for matching
            if host.startswith("www."):
                host = host[4:]
            return host.lower()
        except Exception:
            return ""

    @staticmethod
    def _canonicalize(url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url)
        # Remove fragment, normalize trailing slash
        canonical = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
        if parsed.query:
            canonical += f"?{parsed.query}"
        return canonical.lower()

    @staticmethod
    def _title_from_url(url: str) -> str:
        """Generate a human-readable title from a URL path."""
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            return "Home"
        # Take last path segment, clean it up
        segment = path.split("/")[-1]
        segment = segment.rsplit(".", 1)[0]  # Remove extension
        segment = re.sub(r"[-_]+", " ", segment)
        return segment.title()
