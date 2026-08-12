"""
CourseSync — Structured Content Schemas

AI-layer output models (PRD §9.3).
"""

from __future__ import annotations

from pydantic import BaseModel

from app.schemas.course import ContentType


class ClassificationResult(BaseModel):
    """Result of LLM content classification (fallback path)."""
    content_type: ContentType
    confidence: float = 0.0
    reasoning: str | None = None


class StructuredContent(BaseModel):
    """AI-structured representation of a page (PRD §9.3).

    Empty arrays/strings when source doesn't contain
    the information — never fabricate (FR-6.2).
    """
    title: str
    course: str
    module: str
    content_type: ContentType
    learning_objectives: list[str] = []
    key_concepts: list[str] = []
    definitions: list[dict] = []       # [{"term": "...", "definition": "..."}]
    examples: list[str] = []
    important_formulas: list[str] = []
    prerequisites: list[str] = []
    quiz_topics: list[str] = []
    summary: str = ""
    source_url: str = ""


class QuizQuestion(BaseModel):
    """Extracted quiz question."""
    question: str
    options: list[str] = []
    answer: str | None = None
    explanation: str | None = None
    source_url: str = ""
