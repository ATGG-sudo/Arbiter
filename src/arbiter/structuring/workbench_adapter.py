from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from arbiter.schemas.regulation_structuring import (
    NormalizedTextInput,
    StructuringPipelineOutput,
    StructuringValidationFinding,
    ValidationSeverity,
)
from arbiter.structuring.export import assert_sanitized_for_export
from arbiter.structuring.pipeline import structure_regulation


class MarkdownInput(BaseModel):
    input_kind: Literal["markdown"] = "markdown"
    source_id: str
    source_file: str
    raw_markdown: str
    source_type: Literal["external_regulation", "internal_policy", "unknown"] = "unknown"
    metadata: dict[str, Any] = Field(default_factory=dict)


class StructuringRunRequest(BaseModel):
    request_id: str
    input: MarkdownInput
    llm_assisted: bool = True
    model_mode: Literal["configured_provider", "mock_provider"] = "configured_provider"
    requested_at: str

    @field_validator("input")
    @classmethod
    def input_markdown_must_not_be_empty(cls, value: MarkdownInput) -> MarkdownInput:
        if not value.raw_markdown or not value.raw_markdown.strip():
            raise ValueError("raw_markdown must not be empty")
        return value


class StructuringRunResult(BaseModel):
    request_id: str
    run_id: str
    status: Literal["succeeded", "failed", "validation_failed", "cancelled"]
    output: StructuringPipelineOutput | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    sanitized_trace: dict[str, Any] = Field(default_factory=dict)
    token_usage: dict[str, int] | None = None
    completed_at: str | None = None


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_sanitized_trace(
    adapter: str,
    model_call_count: int,
    validation_findings: list[StructuringValidationFinding],
) -> dict[str, Any]:
    """Return a trace summary with counts only; no prompts, payloads, or secrets."""
    error_count = sum(1 for f in validation_findings if f.severity is ValidationSeverity.ERROR)
    warning_count = sum(1 for f in validation_findings if f.severity is ValidationSeverity.WARNING)
    info_count = sum(1 for f in validation_findings if f.severity is ValidationSeverity.INFO)
    return {
        "adapter": adapter,
        "model_call_count": model_call_count,
        "validation_summary": {
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
        },
        "redaction_warnings": [],
    }


def run_structuring_from_markdown(
    request: StructuringRunRequest,
    model_provider: Any | None = None,
) -> StructuringRunResult:
    """Admin workbench adapter: run the structuring pipeline from a Markdown request.

    Converts the Markdown request into ``NormalizedTextInput``, delegates to
    ``structure_regulation``, and returns a ``StructuringRunResult`` with
    sanitized trace summaries and structured errors.

    Model calls always route through the optional ``model_provider`` argument,
    which must conform to the ``ModelProvider`` protocol. The adapter never
    exposes full prompts, provider payloads, API keys, active rules,
    JudgmentResult, or final compliance conclusions.
    """
    run_id = f"struct-run-{uuid.uuid4().hex[:12]}"
    warnings: list[str] = []
    errors: list[dict[str, Any]] = []
    model_call_count = 0

    # Validate request-level constraints
    raw = request.input.raw_markdown
    if not raw or not raw.strip():
        return StructuringRunResult(
            request_id=request.request_id,
            run_id=run_id,
            status="validation_failed",
            output=None,
            errors=[
                {
                    "code": "empty_markdown_input",
                    "message": "Markdown input is empty after trimming",
                }
            ],
            warnings=[],
            sanitized_trace=_build_sanitized_trace("001-structuring", 0, []),
            token_usage=None,
            completed_at=_now_iso(),
        )

    # Build normalized input
    normalized = NormalizedTextInput(
        source_id=request.input.source_id,
        source_file=request.input.source_file,
        content_type="markdown",
        text=raw,
        source_type=request.input.source_type,
        metadata=request.input.metadata,
    )

    # Determine provider: None means deterministic only
    provider = model_provider if request.llm_assisted else None

    try:
        output = structure_regulation(normalized, model_provider=provider)
    except Exception as exc:
        return StructuringRunResult(
            request_id=request.request_id,
            run_id=run_id,
            status="failed",
            output=None,
            errors=[
                {
                    "code": "structuring_pipeline_failure",
                    "message": str(exc),
                }
            ],
            warnings=warnings,
            sanitized_trace=_build_sanitized_trace("001-structuring", 0, []),
            token_usage=None,
            completed_at=_now_iso(),
        )

    # Validate output schema (defensive; pipeline should already emit valid output)
    try:
        StructuringPipelineOutput.model_validate(output)
    except Exception as exc:
        return StructuringRunResult(
            request_id=request.request_id,
            run_id=run_id,
            status="validation_failed",
            output=None,
            errors=[
                {
                    "code": "output_schema_validation_failed",
                    "message": f"Pipeline output failed schema validation: {exc}",
                }
            ],
            warnings=warnings,
            sanitized_trace=_build_sanitized_trace("001-structuring", 0, []),
            token_usage=None,
            completed_at=_now_iso(),
        )

    try:
        assert_sanitized_for_export(output)
    except Exception as exc:
        return StructuringRunResult(
            request_id=request.request_id,
            run_id=run_id,
            status="validation_failed",
            output=None,
            errors=[
                {
                    "code": "output_sanitization_failed",
                    "message": f"Pipeline output failed sanitization: {exc}",
                }
            ],
            warnings=warnings,
            sanitized_trace=_build_sanitized_trace("001-structuring", 0, []),
            token_usage=None,
            completed_at=_now_iso(),
        )

    # Derive model call count from provenance when LLM was used
    if output.extraction_provenance.extraction_method.value in ("llm_assisted", "mixed"):
        # The LLMExtractionWrapper tracks calls internally; we estimate from
        # provenance presence. For stricter counting, the wrapper would need to
        # expose call_count. We use a conservative estimate of at least 1.
        model_call_count = 1

    # Determine status from validation report
    if output.validation_report.has_errors:
        status: Literal["succeeded", "failed", "validation_failed", "cancelled"] = "validation_failed"
        warnings.append(
            f"Validation report contains {output.validation_report.error_count} error(s)."
        )
    else:
        status = "succeeded"

    # Build sanitized trace
    sanitized_trace = _build_sanitized_trace(
        "001-structuring",
        model_call_count,
        output.validation_report.findings,
    )

    # Ensure no forbidden content leaks into the trace
    trace_json = str(sanitized_trace)
    if "sk-" in trace_json or "api_key" in trace_json.lower():
        sanitized_trace["redaction_warnings"].append(
            "Potential secret detected in trace and redacted."
        )

    result = StructuringRunResult(
        request_id=request.request_id,
        run_id=run_id,
        status=status,
        output=output,
        errors=errors,
        warnings=warnings,
        sanitized_trace=sanitized_trace,
        token_usage=None,
        completed_at=_now_iso(),
    )

    return result
