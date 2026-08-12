"""
CourseSync — Storage Service (Phase 6)

Manages filesystem reads/writes for raw markdown and exports.
Keeps data organization clean: data/raw/{course_id}/, data/exports/{course_id}/.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.config import RAW_DIR, PROCESSED_DIR, EXPORTS_DIR

logger = logging.getLogger(__name__)


class StorageService:
    """Filesystem storage for course content and exports."""

    def __init__(self):
        # Ensure base directories exist
        for d in (RAW_DIR, PROCESSED_DIR, EXPORTS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    # ── Raw Markdown ────────────────────────────────────

    def save_raw_markdown(
        self,
        course_id: str,
        page_id: str,
        content: str,
        metadata: dict | None = None,
    ) -> Path:
        """Save raw scraped markdown to filesystem."""
        course_dir = RAW_DIR / course_id
        course_dir.mkdir(parents=True, exist_ok=True)

        # Save markdown
        md_path = course_dir / f"{page_id}.md"
        md_path.write_text(content, encoding="utf-8")

        # Save metadata alongside
        if metadata:
            meta_path = course_dir / f"{page_id}.meta.json"
            meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        logger.debug("Saved raw markdown: %s", md_path)
        return md_path

    def load_raw_markdown(self, course_id: str, page_id: str) -> str | None:
        """Load raw markdown from filesystem."""
        md_path = RAW_DIR / course_id / f"{page_id}.md"
        if md_path.exists():
            return md_path.read_text(encoding="utf-8")
        return None

    def list_raw_files(self, course_id: str) -> list[dict]:
        """List all raw markdown files for a course."""
        course_dir = RAW_DIR / course_id
        if not course_dir.exists():
            return []

        files = []
        for md_file in sorted(course_dir.glob("*.md")):
            meta_file = course_dir / f"{md_file.stem}.meta.json"
            metadata = {}
            if meta_file.exists():
                try:
                    metadata = json.loads(meta_file.read_text(encoding="utf-8"))
                except Exception:
                    pass

            files.append({
                "filename": md_file.name,
                "page_id": md_file.stem,
                "size_bytes": md_file.stat().st_size,
                "metadata": metadata,
            })

        return files

    # ── Processed Content ───────────────────────────────

    def save_processed(self, course_id: str, page_id: str, content_json: str) -> Path:
        """Save AI-structured content."""
        course_dir = PROCESSED_DIR / course_id
        course_dir.mkdir(parents=True, exist_ok=True)
        path = course_dir / f"{page_id}.json"
        path.write_text(content_json, encoding="utf-8")
        return path

    # ── Exports ─────────────────────────────────────────

    def save_export(self, course_id: str, filename: str, content: str) -> Path:
        """Save an export file (markdown)."""
        course_dir = EXPORTS_DIR / course_id
        course_dir.mkdir(parents=True, exist_ok=True)
        path = course_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info("Saved export: %s", path)
        return path

    def list_exports(self, course_id: str) -> list[dict]:
        """List all export files for a course."""
        course_dir = EXPORTS_DIR / course_id
        if not course_dir.exists():
            return []

        files = []
        for f in sorted(course_dir.iterdir()):
            if f.is_file():
                files.append({
                    "filename": f.name,
                    "size_bytes": f.stat().st_size,
                    "path": str(f),
                })

        return files

    def get_export_path(self, course_id: str, filename: str) -> Path | None:
        """Get the full path to an export file."""
        path = EXPORTS_DIR / course_id / filename
        if path.exists() and path.is_file():
            return path
        return None

    def delete_course(self, course_id: str) -> None:
        """Delete all physical files associated with a course."""
        import shutil
        for d in (RAW_DIR, PROCESSED_DIR, EXPORTS_DIR):
            course_dir = d / course_id
            if course_dir.exists():
                try:
                    shutil.rmtree(course_dir)
                    logger.info("Deleted course directory: %s", course_dir)
                except Exception as e:
                    logger.error("Failed to delete directory %s: %s", course_dir, e)
