from __future__ import annotations

import os
from typing import Any

import pytest

from arbiter.schemas.regulation_structuring import (
    DocumentClassificationDraft,
    DocumentSourceType,
)


def _clear_llm_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in tuple(os.environ):
        if name.startswith("ARBITER_LLM_") or name.startswith("DEEPSEEK_"):
            monkeypatch.delenv(name, raising=False)
    for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL"):
        monkeypatch.delenv(name, raising=False)


def test_default_llm_settings_build_disabled_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    from arbiter.llm import DisabledModelProvider, LLMProviderSettings, build_model_provider

    _clear_llm_env(monkeypatch)

    settings = LLMProviderSettings.from_env()
    provider = build_model_provider(settings)

    assert settings.provider == "none"
    assert isinstance(provider, DisabledModelProvider)
    assert (
        provider.structured_output(
            schema=DocumentClassificationDraft,
            prompt="Classify this document",
            context={},
        )
        is None
    )


def test_deepseek_settings_use_openai_compatible_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from arbiter.llm import LLMProviderSettings

    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("ARBITER_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    settings = LLMProviderSettings.from_env()

    assert settings.provider == "deepseek"
    assert settings.api_key == "test-key"
    assert settings.base_url == "https://api.deepseek.com"
    assert settings.model == "deepseek-chat"


def test_live_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from arbiter.llm import LLMProviderSettings, build_model_provider

    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("ARBITER_LLM_PROVIDER", "openai")

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        build_model_provider(LLMProviderSettings.from_env())


def test_openai_compatible_provider_validates_structured_output() -> None:
    from arbiter.llm import OpenAICompatibleModelProvider

    captured: dict[str, Any] = {}

    def transport(payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
        captured["payload"] = payload
        captured["headers"] = headers
        return {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"source_type":"external_regulation",'
                            '"issuer_type":"government_regulator",'
                            '"categories":[],"topic_tags":["disclosure"],'
                            '"classification_tags":[],"evidence_text":["notice"],'
                            '"ambiguity_notes":[]}'
                        )
                    }
                }
            ]
        }

    provider = OpenAICompatibleModelProvider(
        api_key="test-key",
        base_url="https://example.test",
        model="test-model",
        transport=transport,
    )

    result = provider.structured_output(
        schema=DocumentClassificationDraft,
        prompt="Classify this document",
        context={"document_id": "doc-1"},
    )

    assert result.source_type is DocumentSourceType.EXTERNAL_REGULATION
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    assert captured["payload"]["model"] == "test-model"
    assert captured["payload"]["response_format"] == {"type": "json_object"}
    assert "document_id" in captured["payload"]["messages"][0]["content"]


def test_openai_compatible_provider_rejects_schema_invalid_output() -> None:
    from pydantic import ValidationError

    from arbiter.llm import OpenAICompatibleModelProvider

    provider = OpenAICompatibleModelProvider(
        api_key="test-key",
        base_url="https://example.test",
        model="test-model",
        transport=lambda _payload, _headers: {
            "choices": [{"message": {"content": '{"source_type":"invalid"}'}}]
        },
    )

    with pytest.raises(ValidationError):
        provider.structured_output(
            schema=DocumentClassificationDraft,
            prompt="Classify this document",
            context={},
        )


def test_deepseek_settings_collect_optional_reasoning_knobs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from arbiter.llm import LLMProviderSettings, OpenAICompatibleModelProvider

    _clear_llm_env(monkeypatch)
    monkeypatch.setenv("ARBITER_LLM_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_THINKING_ENABLED", "true")
    monkeypatch.setenv("DEEPSEEK_REASONING_EFFORT", "low")

    settings = LLMProviderSettings.from_env()
    provider = OpenAICompatibleModelProvider(
        api_key=settings.required_api_key(),
        base_url=settings.base_url,
        model=settings.model,
        request_options=settings.request_options,
        transport=lambda payload, _headers: {
            "choices": [
                {
                    "message": {
                        "content": (
                            '{"source_type":"external_regulation",'
                            '"issuer_type":"government_regulator",'
                            '"categories":[],"topic_tags":[],"classification_tags":[],'
                            '"evidence_text":[],"ambiguity_notes":[]}'
                        )
                    }
                }
            ]
        },
    )

    provider.structured_output(
        schema=DocumentClassificationDraft,
        prompt="Classify this document",
        context={},
    )

    assert settings.request_options == {
        "deepseek_thinking_enabled": True,
        "reasoning_effort": "low",
    }
