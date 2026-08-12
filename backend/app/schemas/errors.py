"""
CourseSync — Error Schemas

Single consistent error envelope used across all API endpoints (PRD §10).
"""

from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Consistent error envelope for all API error responses."""
    error: str
    detail: str | None = None
    status_code: int


class ValidationErrorDetail(BaseModel):
    """Individual field validation error."""
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    """Validation error with per-field details."""
    error: str = "Validation Error"
    detail: list[ValidationErrorDetail]
    status_code: int = 422
