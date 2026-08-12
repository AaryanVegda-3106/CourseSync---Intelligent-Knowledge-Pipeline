"""
CourseSync — Nemotron Provider (Phase 8)

LLM provider using NVIDIA NIM's OpenAI-compatible endpoint.
Model, base URL, and API key are environment-configured (PRD §6.3).
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


class NemotronProvider(LLMProvider):
    """NVIDIA Nemotron LLM provider via NIM (OpenAI-compatible)."""

    def __init__(self, api_key: str, base_url: str, model: str):
        if not api_key:
            raise LLMError("Nemotron API key is required", provider="nemotron")
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    base_url=self._base_url,
                    api_key=self._api_key,
                )
            except ImportError:
                raise LLMError(
                    "openai package not installed. Run: pip install openai",
                    provider="nemotron",
                )
        return self._client

    async def classify(self, content: str, context: dict) -> ClassificationResult:
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
            logger.error("Nemotron classification failed: %s", e)
            return ClassificationResult(
                content_type=ContentType.OTHER,
                confidence=0.0,
                reasoning=f"Classification failed: {e}",
            )

    async def structure(self, content: str, context: dict) -> StructuredContent:
        user_prompt = STRUCTURING_USER_PROMPT.format(
            course_name=context.get("course_name", "Unknown"),
            module_name=context.get("module_name", "Unknown"),
            title=context.get("title", "Unknown"),
            url=context.get("url", ""),
            content=content[:8000],
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
            logger.error("Nemotron structuring failed: %s", e)
            raise LLMError(f"Structuring failed: {e}", provider="nemotron")

    async def summarize(self, content: str, context: dict) -> str:
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
            logger.error("Nemotron summarization failed: %s", e)
            return ""

    async def _generate(self, system: str, user: str) -> str:
        """Generate a response via the OpenAI-compatible endpoint."""
        client = self._get_client()

        try:
            response = await client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.2,
                max_tokens=2048,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMError(
                f"Nemotron API call failed: {e}",
                provider="nemotron",
                detail=str(e),
            )

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            raise
