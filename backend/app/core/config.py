"""
CourseSync — Core Configuration

Reads environment variables via pydantic-settings.
All secrets stay in .env, never hard-coded.
"""

from __future__ import annotations

import os
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


# ── Paths ────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]  # coursesync/

if os.environ.get("VERCEL"):
    DATA_DIR = Path("/tmp/data")
else:
    DATA_DIR = PROJECT_ROOT / "data"

RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"

env_file_path = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings sourced from environment variables."""

    model_config = SettingsConfigDict(
        env_file=str(env_file_path) if env_file_path.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────
    app_env: str = "development"
    log_level: str = "INFO"

    # ── Firecrawl ────────────────────────────────────────
    firecrawl_api_key: str = ""

    # ── LLM — provider selection ─────────────────────────
    llm_provider: str = "gemini"  # "nemotron" | "gemini"

    # ── LLM — Nemotron (NVIDIA NIM, OpenAI-compatible) ──
    nemotron_api_key: str = ""
    nemotron_base_url: str = "https://integrate.api.nvidia.com/v1"
    nemotron_model: str = "nvidia/nemotron-3.5-lightning-30b"

    # ── LLM — Gemini ────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # ── Database ─────────────────────────────────────────
    database_url: str = f"sqlite:///{DATA_DIR / 'coursesync.db'}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
