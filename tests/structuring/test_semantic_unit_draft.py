from __future__ import annotations

from arbiter.schemas.regulation_structuring import (
    HierarchyPath,
    NormalizedTextInput,
    ReviewStatus,
    SemanticUnitDraft,
    SourceLocation,
)
from arbiter.structuring.llm_extraction import LLMExtractionWrapper
from arbiter.structuring.pipeline import structure_regulation


def test_semantic_draft_defaults_to_needs_review() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    for unit in output.units:
        assert unit.semantic_draft.review_status is ReviewStatus.NEEDS_REVIEW


def test_semantic_draft_fields_are_empty_when_no_llm() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    for unit in output.units:
        assert unit.semantic_draft.definitions == []
        assert unit.semantic_draft.obligations == []
        assert unit.semantic_draft.trigger_events == []
        assert unit.semantic_draft.required_actions == []
        assert unit.semantic_draft.prohibited_actions == []
        assert unit.semantic_draft.deadlines == []
        assert unit.semantic_draft.thresholds == []
        assert unit.semantic_draft.subject_scope == []
        assert unit.semantic_draft.object_scope == []
        assert unit.semantic_draft.reporting_obligations == []


def test_pipeline_stays_deterministic_when_no_llm_response(mock_model_provider) -> None:
    text = "Article 1\nThe manager must report within 3 days."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp, model_provider=mock_model_provider)

    # No enrichment response was provided, so the method stays deterministic.
    assert output.extraction_provenance.extraction_method.value == "deterministic"


def test_llm_enrichment_changes_method_to_mixed_when_validated(mock_model_provider) -> None:
    text = "Article 1\nThe manager must report within 3 days."
    inp = NormalizedTextInput(
        source_id="t",
        source_file="t.txt",
        content_type="normalized_text",
        text=text,
    )
    mock_model_provider.queue_response(
        {
            "source_type": "external_regulation",
            "review_status": "needs_review",
        }
    )
    output = structure_regulation(inp, model_provider=mock_model_provider)

    assert output.extraction_provenance.extraction_method.value == "mixed"
    assert mock_model_provider.calls


def test_llm_wrapper_rejects_invalid_semantic_payload(mock_model_provider) -> None:
    mock_model_provider.queue_response({"review_status": "not_a_valid_status"})
    wrapper = LLMExtractionWrapper(mock_model_provider)
    from arbiter.schemas.regulation_structuring import RegulationUnitDraft

    unit = RegulationUnitDraft(
        unit_id="u1",
        document_id="doc-1",
        order_index=0,
        source_id="s1",
        source_file="f.txt",
        source_location=SourceLocation(),
        hierarchy=HierarchyPath(),
        original_text="text",
        semantic_draft=SemanticUnitDraft(),
    )
    enriched = wrapper.enrich_semantic_draft(unit)

    # Should fall back to the original draft and record a finding
    assert enriched.semantic_draft.review_status is ReviewStatus.NEEDS_REVIEW
    assert any(f.code == "llm_schema_validation_failure" for f in wrapper.findings)
