from __future__ import annotations

import pytest

from arbiter.cli.server import LLMProviderNotConfigured, _build_provider_for_request
from arbiter.llm.settings import LLMProviderSettings
from arbiter.structuring.workbench_adapter import MarkdownInput, StructuringRunRequest


def _request(*, llm_assisted: bool) -> StructuringRunRequest:
    return StructuringRunRequest(
        request_id="req-001",
        input=MarkdownInput(
            input_kind="markdown",
            source_id="src-001",
            source_file="policy.md",
            raw_markdown="# Policy\n\nArticle 1\nContent.",
            source_type="internal_policy",
        ),
        llm_assisted=llm_assisted,
        model_mode="configured_provider",
        requested_at="2026-05-14T00:00:00Z",
    )


def test_llm_request_requires_configured_live_provider() -> None:
    with pytest.raises(LLMProviderNotConfigured):
        _build_provider_for_request(
            _request(llm_assisted=True),
            LLMProviderSettings(provider="none"),
        )


def test_non_llm_request_uses_deterministic_provider_boundary() -> None:
    provider = _build_provider_for_request(
        _request(llm_assisted=False),
        LLMProviderSettings(provider="none"),
    )

    assert provider is None
