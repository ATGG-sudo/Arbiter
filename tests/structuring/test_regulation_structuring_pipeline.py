from __future__ import annotations

import pytest

from arbiter.schemas.regulation_structuring import (
    DocumentSourceType,
    ExtractionMethod,
    NormalizedTextInput,
    ParseStatus,
    ReviewStatus,
    StructuringPipelineOutput,
)
from arbiter.structuring.pipeline import structure_regulation


def test_pipeline_returns_draft_document_and_units_for_markdown() -> None:
    text = "# Example Regulation\n\n## Chapter 1\n\nArticle 1 Scope\n\nContent."
    inp = NormalizedTextInput(
        source_id="md",
        source_file="reg.md",
        content_type="markdown",
        text=text,
    )
    output = structure_regulation(inp)

    assert isinstance(output, StructuringPipelineOutput)
    assert output.document.parse_status is ParseStatus.NEEDS_REVIEW
    assert len(output.units) > 0
    assert output.validation_report.document_id == output.document.document_id


def test_pipeline_returns_draft_document_and_units_for_text() -> None:
    text = "1. Scope\nThis applies.\n\n2. Action\nDo this."
    inp = NormalizedTextInput(
        source_id="txt",
        source_file="reg.txt",
        content_type="normalized_text",
        text=text,
    )
    output = structure_regulation(inp)

    assert output.document.parse_status is ParseStatus.NEEDS_REVIEW
    assert len(output.units) >= 2


def test_pipeline_output_contains_no_judgment_or_rule_artifacts() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
    )
    output = structure_regulation(inp)

    raw = output.model_dump_json()
    assert "JudgmentResult" not in raw
    assert "RulePack" not in raw
    assert "RuleItem" not in raw


def test_pipeline_rejects_empty_text_at_intake() -> None:
    with pytest.raises(ValueError):
        NormalizedTextInput(
            source_id="t",
            source_file="t.txt",
            content_type="normalized_text",
            text="   ",
        )


def test_pipeline_preserves_source_type_in_classification() -> None:
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text="Article 1\nContent.",
        source_type=DocumentSourceType.EXTERNAL_REGULATION,
    )
    output = structure_regulation(inp)

    assert output.document.classification.source_type is DocumentSourceType.EXTERNAL_REGULATION
    assert output.document.classification.review_status is ReviewStatus.NEEDS_REVIEW


def test_pipeline_maps_document_number_from_metadata() -> None:
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text="Article 1\nContent.",
        metadata={"document_number": "GB/T 2025-001"},
    )
    output = structure_regulation(inp)

    assert output.document.document_number == "GB/T 2025-001"


def test_pipeline_maps_category_tags_to_document_categories() -> None:
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text="Article 1\nContent.",
        metadata={"category_tags": ["investment", "compliance"]},
    )
    output = structure_regulation(inp)

    categories = output.document.classification.categories
    assert len(categories) == 2
    labels = {c.category_label for c in categories}
    assert "investment" in labels
    assert "compliance" in labels
    assert all(c.category_scheme == "custom" for c in categories)


def test_pipeline_allows_null_document_number_and_empty_categories() -> None:
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text="Article 1\nContent.",
    )
    output = structure_regulation(inp)

    assert output.document.document_number is None
    assert output.document.classification.categories == []


def test_pipeline_stays_deterministic_when_provider_returns_none(mock_model_provider) -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
    )
    output = structure_regulation(inp, model_provider=mock_model_provider)

    assert output.extraction_provenance.extraction_method is ExtractionMethod.DETERMINISTIC
    assert output.extraction_provenance.prompt_contract_version is None
    assert output.extraction_provenance.model_trace_id is None


def test_pipeline_uses_mixed_after_validated_llm_enrichment(mock_model_provider) -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
    )
    mock_model_provider.queue_response(
        {
            "source_type": "external_regulation",
            "issuer_type": "government_regulator",
            "review_status": "needs_review",
        }
    )
    output = structure_regulation(inp, model_provider=mock_model_provider)

    assert output.extraction_provenance.extraction_method is ExtractionMethod.MIXED
    assert output.extraction_provenance.prompt_contract_version == "structuring-v1"
    assert output.extraction_provenance.model_trace_id == "trace-llm"
    assert mock_model_provider.calls


def test_pipeline_stays_deterministic_when_llm_validation_fails(mock_model_provider) -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
    )
    mock_model_provider.queue_response(
        {
            "source_type": "invalid_type",
            "review_status": "needs_review",
        }
    )
    output = structure_regulation(inp, model_provider=mock_model_provider)

    assert output.extraction_provenance.extraction_method is ExtractionMethod.DETERMINISTIC
    assert any(
        f.code == "llm_schema_validation_failure"
        for f in output.validation_report.findings
    )


def test_pipeline_merges_llm_dependency_edges_into_graph(mock_model_provider) -> None:
    text = "Article 1\nSee Article 2.\n\nArticle 2\nContent."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
    )
    # Queue responses for: classification, semantic unit 0, semantic unit 1, dependency
    mock_model_provider.queue_response(None)
    mock_model_provider.queue_response(None)
    mock_model_provider.queue_response(None)
    mock_model_provider.queue_response(
        {
            "edge_id": "doc-t-edge-llm",
            "document_id": "doc-t",
            "from_unit_id": "doc-t-unit-0",
            "to_unit_id": "doc-t-unit-1",
            "target_scope": "same_document",
            "resolution_status": "resolved",
            "relation_kind": "cross_reference",
            "evidence_text": "See Article 2.",
            "review_status": "needs_review",
        }
    )
    output = structure_regulation(inp, model_provider=mock_model_provider)

    assert output.extraction_provenance.extraction_method is ExtractionMethod.MIXED
    edge_ids = {e.edge_id for e in output.dependency_graph.dependency_edges}
    assert "doc-t-edge-llm" in edge_ids
