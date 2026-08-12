"""
CourseSync — LLM Provider Abstraction (Phase 7)

Abstract base class defining the contract for all LLM providers (PRD §6.3).
Business logic never hard-codes a specific model/vendor (AP2).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.schemas.structured import ClassificationResult, StructuredContent


class LLMProvider(ABC):
    """Abstract LLM provider interface.

    All LLM interactions in CourseSync go through this interface.
    Implementations: NemotronProvider, GeminiProvider.
    """

    @abstractmethod
    async def classify(self, content: str, context: dict) -> ClassificationResult:
        """Classify content into a ContentType.

        Used as a fallback when deterministic classification is inconclusive (FR-5.3).
        """
        ...

    @abstractmethod
    async def structure(self, content: str, context: dict) -> StructuredContent:
        """Transform raw content into StructuredContent schema (FR-6.1).

        Must NOT hallucinate fields — any field absent from source content
        shall be returned empty, never invented (FR-6.2).
        """
        ...

    @abstractmethod
    async def summarize(self, content: str, context: dict) -> str:
        """Generate a concise summary of the content."""
        ...
