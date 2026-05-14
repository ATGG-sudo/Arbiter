from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Mapping


_TRUE_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class LLMProviderSettings:
    """Environment-derived LLM provider settings.

    Defaults keep Arbiter offline. Live providers are selected explicitly with
    ARBITER_LLM_PROVIDER and are not wired into runtime code by this settings
    object.
    """

    provider: str = "none"
    model: str = ""
    base_url: str = ""
    api_key: str | None = None
    api_key_env_var: str | None = None
    timeout_seconds: float = 30.0
    request_options: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_env(
        cls,
        env: Mapping[str, str] | None = None,
    ) -> "LLMProviderSettings":
        values = env if env is not None else os.environ
        provider = values.get("ARBITER_LLM_PROVIDER", "none").strip().lower()
        provider = provider.replace("-", "_")

        timeout_seconds = float(values.get("ARBITER_LLM_TIMEOUT_SECONDS", "30"))

        if provider == "none":
            return cls(provider="none", timeout_seconds=timeout_seconds)

        if provider == "openai":
            return cls(
                provider="openai",
                model=(
                    values.get("ARBITER_LLM_MODEL")
                    or values.get("OPENAI_MODEL")
                    or "gpt-4.1-mini"
                ),
                base_url=values.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
                api_key=values.get("OPENAI_API_KEY"),
                api_key_env_var="OPENAI_API_KEY",
                timeout_seconds=timeout_seconds,
            )

        if provider == "deepseek":
            return cls(
                provider="deepseek",
                model=(
                    values.get("ARBITER_LLM_MODEL")
                    or values.get("DEEPSEEK_MODEL")
                    or "deepseek-chat"
                ),
                base_url=values.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
                api_key=values.get("DEEPSEEK_API_KEY"),
                api_key_env_var="DEEPSEEK_API_KEY",
                timeout_seconds=timeout_seconds,
                request_options=_deepseek_request_options(values),
            )

        if provider == "openai_compatible":
            return cls(
                provider="openai_compatible",
                model=values.get("ARBITER_LLM_MODEL", ""),
                base_url=values.get("ARBITER_LLM_BASE_URL", ""),
                api_key=values.get("ARBITER_LLM_API_KEY"),
                api_key_env_var="ARBITER_LLM_API_KEY",
                timeout_seconds=timeout_seconds,
            )

        raise ValueError(
            "ARBITER_LLM_PROVIDER must be one of: none, openai, deepseek, "
            "openai_compatible"
        )

    def required_api_key(self) -> str:
        if self.api_key:
            return self.api_key
        if self.api_key_env_var:
            raise ValueError(
                f"{self.api_key_env_var} is required when "
                f"ARBITER_LLM_PROVIDER={self.provider}"
            )
        raise ValueError("No API key is configured for the selected LLM provider")

    def required_model(self) -> str:
        if self.model.strip():
            return self.model
        raise ValueError("ARBITER_LLM_MODEL is required for this LLM provider")

    def required_base_url(self) -> str:
        if self.base_url.strip():
            return self.base_url
        raise ValueError("ARBITER_LLM_BASE_URL is required for this LLM provider")


def _deepseek_request_options(values: Mapping[str, str]) -> dict[str, Any]:
    options: dict[str, Any] = {}
    thinking_enabled = values.get("DEEPSEEK_THINKING_ENABLED")
    if thinking_enabled and thinking_enabled.strip().lower() in _TRUE_VALUES:
        options["deepseek_thinking_enabled"] = True

    reasoning_effort = values.get("DEEPSEEK_REASONING_EFFORT")
    if reasoning_effort:
        options["reasoning_effort"] = reasoning_effort.strip()

    return options
