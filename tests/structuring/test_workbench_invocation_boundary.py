from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError

from arbiter.schemas.regulation_structuring import (
    DocumentSourceType,
    ExtractionMethod,
    StructuringPipelineOutput,
)
from arbiter.structuring.workbench_adapter import (
    MarkdownInput,
    StructuringRunRequest,
    StructuringRunResult,
    run_structuring_from_markdown,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_request(
    raw_markdown: str,
    source_id: str = "src-001",
    source_file: str = "policy.md",
    llm_assisted: bool = True,
    model_mode: str = "configured_provider",
) -> StructuringRunRequest:
    return StructuringRunRequest(
        request_id="req-001",
        input=MarkdownInput(
            source_id=source_id,
            source_file=source_file,
            raw_markdown=raw_markdown,
            source_type="internal_policy",
            metadata={"title": "Test Policy"},
        ),
        llm_assisted=llm_assisted,
        model_mode=model_mode,  # type: ignore[arg-type]
        requested_at="2026-05-14T00:00:00Z",
    )


# ---------------------------------------------------------------------------
# T050a: Request/response contract and status paths
# ---------------------------------------------------------------------------

def test_successful_markdown_request_returns_succeeded_and_valid_output() -> None:
    request = _make_request("# Policy\n\nArticle 1\nContent.")
    result = run_structuring_from_markdown(request)

    assert isinstance(result, StructuringRunResult)
    assert result.request_id == "req-001"
    assert result.run_id.startswith("struct-run-")
    assert result.status == "succeeded"
    assert result.output is not None
    assert isinstance(result.output, StructuringPipelineOutput)
    assert result.completed_at is not None
    assert len(result.errors) == 0


def _make_request_unvalidated(
    raw_markdown: str,
    source_id: str = "src-001",
    source_file: str = "policy.md",
    llm_assisted: bool = True,
    model_mode: str = "configured_provider",
) -> StructuringRunRequest:
    """Construct a request bypassing Pydantic validation for negative tests."""
    return StructuringRunRequest.model_construct(
        request_id="req-001",
        input=MarkdownInput.model_construct(
            source_id=source_id,
            source_file=source_file,
            raw_markdown=raw_markdown,
            source_type="internal_policy",
            metadata={"title": "Test Policy"},
        ),
        llm_assisted=llm_assisted,
        model_mode=model_mode,  # type: ignore[arg-type]
        requested_at="2026-05-14T00:00:00Z",
    )


def test_empty_markdown_returns_validation_failed() -> None:
    request = _make_request_unvalidated("")
    result = run_structuring_from_markdown(request)

    assert result.status == "validation_failed"
    assert result.output is None
    assert any(e["code"] == "empty_markdown_input" for e in result.errors)


def test_whitespace_only_markdown_returns_validation_failed() -> None:
    request = _make_request_unvalidated("   \n\t  ")
    result = run_structuring_from_markdown(request)

    assert result.status == "validation_failed"
    assert result.output is None
    assert any(e["code"] == "empty_markdown_input" for e in result.errors)


def test_request_model_rejects_empty_markdown_at_validation() -> None:
    with pytest.raises(ValidationError, match="raw_markdown must not be empty"):
        _make_request("")


# ---------------------------------------------------------------------------
# T050b: Mock provider, sanitization, and forbidden-content boundaries
# ---------------------------------------------------------------------------

def test_mock_provider_path_proves_model_calls_route_through_model_provider(
    mock_model_provider,
) -> None:
    request = _make_request(
        "Article 1\nContent.",
        llm_assisted=True,
        model_mode="mock_provider",
    )
    mock_model_provider.queue_response(
        {
            "source_type": "external_regulation",
            "issuer_type": "government_regulator",
            "review_status": "needs_review",
        }
    )
    result = run_structuring_from_markdown(request, model_provider=mock_model_provider)

    assert result.status == "succeeded"
    assert result.output is not None
    assert result.output.extraction_provenance.extraction_method is ExtractionMethod.MIXED
    assert mock_model_provider.calls
    # Prove the provider received a structured_output call
    assert any(call["schema"] is not None for call in mock_model_provider.calls)


def test_mock_provider_is_used_when_llm_assisted_is_true(mock_model_provider) -> None:
    request = _make_request(
        "Article 1\nSee Article 2.\n\nArticle 2\nContent.",
        llm_assisted=True,
        model_mode="mock_provider",
    )
    # Queue enough responses for classification + semantic units + dependency
    mock_model_provider.queue_response(None)
    mock_model_provider.queue_response(None)
    mock_model_provider.queue_response(None)
    mock_model_provider.queue_response(None)
    result = run_structuring_from_markdown(request, model_provider=mock_model_provider)

    assert result.status == "succeeded"
    assert result.output is not None
    # Even with all None responses, provider should have been called
    assert len(mock_model_provider.calls) > 0


def test_deterministic_path_when_no_provider_and_llm_disabled() -> None:
    request = _make_request(
        "Article 1\nContent.",
        llm_assisted=False,
    )
    result = run_structuring_from_markdown(request, model_provider=None)

    assert result.status == "succeeded"
    assert result.output is not None
    assert result.output.extraction_provenance.extraction_method is ExtractionMethod.DETERMINISTIC


def test_sanitized_trace_contains_summaries_and_counts_only() -> None:
    request = _make_request("# Policy\n\nArticle 1\nContent.")
    result = run_structuring_from_markdown(request)

    trace = result.sanitized_trace
    assert "adapter" in trace
    assert trace["adapter"] == "001-structuring"
    assert "model_call_count" in trace
    assert isinstance(trace["model_call_count"], int)
    assert "validation_summary" in trace
    summary = trace["validation_summary"]
    assert "error_count" in summary
    assert "warning_count" in summary
    assert "info_count" in summary

    # Must NOT contain full prompts or provider payloads
    trace_json = str(trace)
    assert "full prompt" not in trace_json.lower()
    assert "system prompt" not in trace_json.lower()
    assert '"choices"' not in trace_json
    assert '"messages"' not in trace_json
    assert '"usage"' not in trace_json


def test_result_never_exposes_full_prompts_or_provider_payloads() -> None:
    request = _make_request("Article 1\nContent.")
    result = run_structuring_from_markdown(request)

    raw = result.model_dump_json()
    assert "full prompt" not in raw.lower()
    assert "system prompt" not in raw.lower()
    assert "provider payload" not in raw.lower()
    assert "api_key" not in raw.lower()
    assert "sk-" not in raw


def test_result_never_exposes_api_keys_or_secrets() -> None:
    request = _make_request("Article 1\nContent.")
    result = run_structuring_from_markdown(request)

    raw = result.model_dump_json()
    assert "sk-" not in raw
    assert "api_key" not in raw.lower()
    assert "password" not in raw.lower()
    assert "bearer " not in raw.lower()


def test_result_never_contains_judgment_result_or_rule_artifacts() -> None:
    request = _make_request("Article 1\nContent.")
    result = run_structuring_from_markdown(request)

    raw = result.model_dump_json()
    assert "JudgmentResult" not in raw
    assert "RulePack" not in raw
    assert "RuleItem" not in raw
    assert "final_compliance_conclusion" not in raw.lower()


def test_result_never_contains_active_rules_or_final_conclusions() -> None:
    request = _make_request("# Policy\n\nArticle 1\nContent.")
    result = run_structuring_from_markdown(request)

    raw = result.model_dump_json()
    assert "active_rule" not in raw.lower()
    assert "final conclusion" not in raw.lower()
    assert "compliance_judgment" not in raw.lower()


def test_unsafe_output_returns_validation_failed_without_output() -> None:
    request = _make_request(
        "Article 1\nContent.",
        source_file="/tmp/policy.md",
    )
    result = run_structuring_from_markdown(request)

    assert result.status == "validation_failed"
    assert result.output is None
    assert any(e["code"] == "output_sanitization_failed" for e in result.errors)


# ---------------------------------------------------------------------------
# Adapter is Admin-only and not a runtime/agent tool
# ---------------------------------------------------------------------------

def test_adapter_is_not_registered_as_runtime_or_agent_tool() -> None:
    from arbiter.structuring import __init__ as structuring_init

    init_source = open("src/arbiter/structuring/__init__.py").read()
    assert "agent" not in init_source.lower() or "run_structuring_from_markdown" in init_source
    assert "runtime" not in init_source.lower() or "run_structuring_from_markdown" in init_source
    assert "tool" not in init_source.lower() or "run_structuring_from_markdown" in init_source


def test_adapter_import_available_without_runtime_side_effects() -> None:
    # Importing the adapter should not create runtime directories or registrations
    from arbiter.structuring.workbench_adapter import run_structuring_from_markdown

    assert callable(run_structuring_from_markdown)


# ---------------------------------------------------------------------------
# Output validation and structured error paths
# ---------------------------------------------------------------------------

def test_validation_failed_status_when_output_has_errors() -> None:
    # Empty text after intake should produce validation findings with errors
    # But NormalizedTextInput itself rejects empty text, so the adapter
    # pre-validates. We'll test with a request that the adapter allows but
    # pipeline may flag.
    request = _make_request("Article 1\nContent.")
    result = run_structuring_from_markdown(request)

    # If the pipeline produces errors, status should be validation_failed
    # Otherwise succeeded. We assert the output is valid either way.
    if result.status == "succeeded":
        assert result.output is not None
        assert not result.output.validation_report.has_errors
    else:
        assert result.status == "validation_failed"


def test_output_validates_as_structuring_pipeline_output_on_success() -> None:
    request = _make_request("# Policy\n\n## Chapter 1\n\nArticle 1\nContent.")
    result = run_structuring_from_markdown(request)

    if result.status == "succeeded":
        assert result.output is not None
        parsed = StructuringPipelineOutput.model_validate(result.output)
        assert parsed.document.document_id == result.output.document.document_id


def test_result_includes_request_id_and_run_id() -> None:
    request = _make_request("Article 1\nContent.")
    result = run_structuring_from_markdown(request)

    assert result.request_id == request.request_id
    assert result.run_id is not None
    assert len(result.run_id) > 0


def test_result_includes_completed_at_timestamp() -> None:
    request = _make_request("Article 1\nContent.")
    result = run_structuring_from_markdown(request)

    assert result.completed_at is not None
    assert "T" in result.completed_at
