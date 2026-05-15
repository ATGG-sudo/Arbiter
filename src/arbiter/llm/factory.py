from __future__ import annotations

from arbiter.llm.base import DisabledModelProvider, ModelProvider
from arbiter.llm.openai_compatible import OpenAICompatibleModelProvider
from arbiter.llm.settings import LLMProviderSettings


def build_model_provider(
    settings: LLMProviderSettings | None = None,
) -> ModelProvider:
    """Build the configured provider without wiring it into any runtime path."""

    resolved = settings or LLMProviderSettings.from_env()
    if resolved.provider == "none":
        return DisabledModelProvider()

    if resolved.provider in {"openai", "deepseek", "openai_compatible"}:
        return OpenAICompatibleModelProvider(
            api_key=resolved.required_api_key(),
            base_url=resolved.required_base_url(),
            model=resolved.required_model(),
            request_options=resolved.request_options,
            timeout_seconds=resolved.timeout_seconds,
            locale=resolved.locale,
        )

    raise ValueError(f"Unsupported LLM provider: {resolved.provider}")
