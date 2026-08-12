"""
CourseSync — Gemini Provider (Phase 8)

LLM provider using Google's Gemini API via google-genai SDK.
"""

from __future__ import annotations

import json
import logging

from app.core.exceptions import LLMError
from app.schemas.course import ContentType
from app.schemas.structured import ClassificationResult, StructuredContent
from app.services.llm.provider import LLMProvider
from app.services.llm.prompts import (
    CLASSIFICATION_SYSTEM_PROMPT, CLASSIFICATION_USER_PROMPT,
    STRUCTURING_SYSTEM_PROMPT, STRUCTURING_USER_PROMPT,
    SUMMARIZE_SYSTEM_PROMPT, SUMMARIZE_USER_PROMPT,
)

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        if not api_key:
            raise LLMError("Gemini API key is required", provider="gemini")
        self._api_key = api_key
        self._model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from google import genai
                self._client = genai.Client(api_key=self._api_key)
            except ImportError:
                raise LLMError(
                    "google-genai package not installed. Run: pip install google-genai",
                    provider="gemini",
                )
        return self._client

    async def classify(self, content: str, context: dict) -> ClassificationResult:
        """Classify content using Gemini (LLM fallback path)."""
        user_prompt = CLASSIFICATION_USER_PROMPT.format(
            title=context.get("title", "Unknown"),
            url=context.get("url", "Unknown"),
            content=content[:2000],
        )

        try:
            response_text = await self._generate(
                system=CLASSIFICATION_SYSTEM_PROMPT,
                user=user_prompt,
            )
            data = self._parse_json(response_text)
            return ClassificationResult(
                content_type=ContentType(data.get("content_type", "other")),
                confidence=float(data.get("confidence", 0.5)),
                reasoning=data.get("reasoning"),
            )
        except Exception as e:
            logger.error("Gemini classification failed: %s", e)
            return ClassificationResult(
                content_type=ContentType.OTHER,
                confidence=0.0,
                reasoning=f"Classification failed: {e}",
            )

    async def structure(self, content: str, context: dict) -> StructuredContent:
        """Structure content using Gemini."""
        user_prompt = STRUCTURING_USER_PROMPT.format(
            course_name=context.get("course_name", "Unknown"),
            module_name=context.get("module_name", "Unknown"),
            title=context.get("title", "Unknown"),
            url=context.get("url", ""),
            content=content[:8000],  # Limit content length
        )

        try:
            response_text = await self._generate(
                system=STRUCTURING_SYSTEM_PROMPT,
                user=user_prompt,
            )
            data = self._parse_json(response_text)

            return StructuredContent(
                title=data.get("title", context.get("title", "Unknown")),
                course=data.get("course", context.get("course_name", "")),
                module=data.get("module", context.get("module_name", "")),
                content_type=ContentType(data.get("content_type", "other")),
                learning_objectives=data.get("learning_objectives", []),
                key_concepts=data.get("key_concepts", []),
                definitions=data.get("definitions", []),
                examples=data.get("examples", []),
                important_formulas=data.get("important_formulas", []),
                prerequisites=data.get("prerequisites", []),
                quiz_topics=data.get("quiz_topics", []),
                summary=data.get("summary", ""),
                source_url=data.get("source_url", context.get("url", "")),
            )
        except Exception as e:
            logger.error("Gemini structuring failed: %s", e)
            raise LLMError(f"Structuring failed: {e}", provider="gemini")

    async def summarize(self, content: str, context: dict) -> str:
        """Summarize content using Gemini."""
        user_prompt = SUMMARIZE_USER_PROMPT.format(
            title=context.get("title", ""),
            content=content[:6000],
        )

        try:
            return await self._generate(
                system=SUMMARIZE_SYSTEM_PROMPT,
                user=user_prompt,
            )
        except Exception as e:
            logger.error("Gemini summarization failed: %s", e)
            return ""

    async def _generate(self, system: str, user: str) -> str:
        """Generate a response from Gemini."""
        import asyncio
        client = self._get_client()

        try:
            response = await asyncio.to_thread(
                client.models.generate_content,
                model=self._model,
                contents=user,
                config={
                    "system_instruction": system,
                    "temperature": 0.2,
                    "max_output_tokens": 4096,
                },
            )
            return response.text or ""
        except Exception as e:
            raise LLMError(f"Gemini API call failed: {e}", provider="gemini", detail=str(e))

    @staticmethod
    def _parse_json(text: str) -> dict:
        """Extract JSON from LLM response, handling markdown code blocks."""
        text = text.strip()
        # Strip markdown code fences
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise
