"""
CourseSync — FastAPI Application

Main entry point. Initializes the database, registers routes,
configures CORS, and sets up error handlers.
"""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings, DATA_DIR, RAW_DIR, PROCESSED_DIR, EXPORTS_DIR
from app.core.database import init_db
from app.core.exceptions import CourseSyncError, NotFoundError, ValidationError
from app.api.routes.courses import router as courses_router


# ── Logging ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(name)-30s │ %(levelname)-8s │ %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("coursesync")


# ── Lifespan ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    settings = get_settings()
    logger.info("CourseSync starting (env=%s)", settings.app_env)

    # Create data directories
    for d in (DATA_DIR, RAW_DIR, PROCESSED_DIR, EXPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    yield

    logger.info("CourseSync shutting down")


# ── App Factory ──────────────────────────────────────────

app = FastAPI(
    title="CourseSync",
    description="AI-powered course ingestion platform — NotebookLM-ready knowledge extraction",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS (allow frontend dev server + Vercel production) ──

_cors_origins = [
    "http://localhost:5173",   # Vite dev server
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Dynamically add Vercel deployment URLs when running on Vercel
_vercel_url = os.environ.get("VERCEL_URL")
if _vercel_url:
    _cors_origins.append(f"https://{_vercel_url}")

_vercel_prod_url = os.environ.get("VERCEL_PROJECT_PRODUCTION_URL")
if _vercel_prod_url:
    _cors_origins.append(f"https://{_vercel_prod_url}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────

app.include_router(courses_router)


# ── Health Check ─────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "coursesync", "version": "0.1.0"}


# ── Error Handlers ───────────────────────────────────────

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": exc.message, "detail": exc.detail, "status_code": 404},
    )


@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": exc.message, "detail": exc.detail, "status_code": 422},
    )


@app.exception_handler(CourseSyncError)
async def coursesync_error_handler(request: Request, exc: CourseSyncError):
    return JSONResponse(
        status_code=500,
        content={"error": exc.message, "detail": exc.detail, "status_code": 500},
    )
