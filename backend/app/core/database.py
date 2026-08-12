"""
CourseSync — SQLite Database Manager

Async SQLite via aiosqlite with schema auto-init.
Repository layer abstraction means this can be swapped
for PostgreSQL without touching business logic (AP3).
"""

from __future__ import annotations

import aiosqlite
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.config import DATA_DIR


DB_PATH = DATA_DIR / "coursesync.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS courses (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    url             TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'created',
    module_count    INTEGER NOT NULL DEFAULT 0,
    page_count      INTEGER NOT NULL DEFAULT 0,
    last_synced_at  TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS modules (
    id          TEXT PRIMARY KEY,
    course_id   TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title       TEXT NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS pages (
    id              TEXT PRIMARY KEY,
    course_id       TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    module_id       TEXT REFERENCES modules(id) ON DELETE SET NULL,
    title           TEXT,
    url             TEXT NOT NULL,
    content_type    TEXT NOT NULL DEFAULT 'other',
    status          TEXT NOT NULL DEFAULT 'discovered',
    content_hash    TEXT,
    scraped_at      TEXT,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ingestion_jobs (
    id                  TEXT PRIMARY KEY,
    course_id           TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    current_stage       TEXT NOT NULL DEFAULT 'mapping',
    pages_discovered    INTEGER NOT NULL DEFAULT 0,
    pages_scraped       INTEGER NOT NULL DEFAULT 0,
    pages_failed        INTEGER NOT NULL DEFAULT 0,
    pages_processed     INTEGER NOT NULL DEFAULT 0,
    files_generated     INTEGER NOT NULL DEFAULT 0,
    started_at          TEXT NOT NULL,
    completed_at        TEXT,
    error               TEXT
);

CREATE TABLE IF NOT EXISTS scraped_content (
    id              TEXT PRIMARY KEY,
    page_id         TEXT NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    course_id       TEXT NOT NULL,
    url             TEXT NOT NULL,
    content_hash    TEXT NOT NULL,
    markdown        TEXT,
    metadata_json   TEXT,
    retrieved_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS structured_content (
    id              TEXT PRIMARY KEY,
    page_id         TEXT NOT NULL REFERENCES pages(id) ON DELETE CASCADE,
    course_id       TEXT NOT NULL,
    content_json    TEXT NOT NULL,
    created_at      TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_scraped_content_url_hash
    ON scraped_content(url, content_hash);

CREATE INDEX IF NOT EXISTS idx_pages_course_id
    ON pages(course_id);

CREATE INDEX IF NOT EXISTS idx_modules_course_id
    ON modules(course_id);

CREATE INDEX IF NOT EXISTS idx_jobs_course_id
    ON ingestion_jobs(course_id);
"""


async def init_db() -> None:
    """Create database directory and initialize schema."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(str(DB_PATH)) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncGenerator[aiosqlite.Connection, None]:
    """Yield an async SQLite connection."""
    db = await aiosqlite.connect(str(DB_PATH))
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON;")
    try:
        yield db
    finally:
        await db.close()
