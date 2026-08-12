"""
CourseSync — LLM Provider Factory

Instantiates the configured LLM provider from environment variables.
"""

from __future__ import annotations

from app.core.config import get_settings
from app.core.exceptions import LLMError
from app.services.llm.provider import LLMProvider


def create_llm_provider() -> LLMProvider:
    """Create the LLM provider configured in environment.

    Returns NemotronProvider or GeminiProvider based on LLM_PROVIDER env var.
    """
    settings = get_settings()
    provider = settings.llm_provider.lower()

    if provider == "gemini":
        from app.services.llm.gemini_provider import GeminiProvider
        return GeminiProvider(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )
    elif provider == "nemotron":
        from app.services.llm.nemotron_provider import NemotronProvider
        return NemotronProvider(
            api_key=settings.nemotron_api_key,
            base_url=settings.nemotron_base_url,
            model=settings.nemotron_model,
        )
    else:
        raise LLMError(f"Unknown LLM provider: {provider}. Use 'gemini' or 'nemotron'.")
