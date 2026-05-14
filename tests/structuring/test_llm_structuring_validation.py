from __future__ import annotations

import pytest
from pydantic import ValidationError

from arbiter.schemas.regulation_structuring import (
    DocumentClassificationDraft,
    DocumentSourceType,
    ReviewStatus,
)


def test_mock_model_provider_validates_structured_output(mock_model_provider) -> None:
    mock_model_provider.queue_response(
        {
            "source_type": "external_regulation",
            "issuer_type": "government_regulator",
            "issuer_name": "Regulator",
            "categories": [],
            "topic_tags": ["disclosure"],
            "classification_tags": [],
            "evidence_text": ["Regulator notice"],
            "confidence": 0.8,
            "ambiguity_notes": [],
        }
    )
    result = mock_model_provider.structured_output(
        schema=DocumentClassificationDraft,
        prompt="Classify this document",
        context={},
    )

    assert result.source_type is DocumentSourceType.EXTERNAL_REGULATION
    assert result.review_status is ReviewStatus.NEEDS_REVIEW
    assert mock_model_provider.calls[0]["schema"] is DocumentClassificationDraft


def test_mock_model_provider_rejects_schema_invalid_output(mock_model_provider) -> None:
    mock_model_provider.queue_response(
        {
            "source_type": "not-a-valid-source-type",
            "issuer_type": "government_regulator",
            "issuer_name": "Regulator",
            "categories": [],
            "topic_tags": [],
            "classification_tags": [],
            "evidence_text": [],
            "ambiguity_notes": [],
        }
    )
    with pytest.raises(ValidationError):
        mock_model_provider.structured_output(
            schema=DocumentClassificationDraft,
            prompt="Classify this document",
            context={},
        )


def test_blocking_provider_prevents_real_model_calls(blocking_model_provider) -> None:
    with pytest.raises(AssertionError, match="Real model calls are forbidden"):
        blocking_model_provider.structured_output(
            schema=DocumentClassificationDraft,
            prompt="Classify this document",
            context={},
        )


def test_llm_wrapper_only_supplements_deterministic_candidates(mock_model_provider) -> None:
    from arbiter.structuring.llm_extraction import LLMExtractionWrapper
    from arbiter.schemas.regulation_structuring import SemanticUnitDraft

    mock_model_provider.queue_response(
        {"unit_type": "obligation", "obligations": ["report"], "review_status": "needs_review"}
    )
    wrapper = LLMExtractionWrapper(mock_model_provider)
    result = wrapper._call_or_find(
        SemanticUnitDraft,
        "Extract semantics",
        {"unit_id": "u1"},
        "test",
    )
    assert result is not None
    assert result.obligations == ["report"]
    assert not wrapper.findings


def test_llm_wrapper_rejects_invalid_model_output(mock_model_provider) -> None:
    from arbiter.structuring.llm_extraction import LLMExtractionWrapper
    from arbiter.schemas.regulation_structuring import SemanticUnitDraft

    mock_model_provider.queue_response({"review_status": "not_valid"})
    wrapper = LLMExtractionWrapper(mock_model_provider)
    result = wrapper._call_or_find(
        SemanticUnitDraft,
        "Extract semantics",
        {"unit_id": "u1"},
        "test",
    )
    assert result is None
    assert any(f.code == "llm_schema_validation_failure" for f in wrapper.findings)


def test_llm_wrapper_creates_validation_finding_for_ambiguous_proposal(mock_model_provider) -> None:
    from arbiter.structuring.llm_extraction import LLMExtractionWrapper
    from arbiter.schemas.regulation_structuring import DocumentClassificationDraft

    mock_model_provider.queue_response({"source_type": "invalid_type"})
    wrapper = LLMExtractionWrapper(mock_model_provider)
    result = wrapper.enrich_classification(
        DocumentClassificationDraft(),
        document_title="Test",
        document_text="Some text",
    )
    assert result.review_status is ReviewStatus.NEEDS_REVIEW
    finding = next(f for f in wrapper.findings if f.code == "llm_schema_validation_failure")
    assert finding.stage == "document"
    assert finding.target_type == "document"


def test_llm_wrapper_rejects_wrong_schema_instance_from_provider() -> None:
    from arbiter.schemas.regulation_structuring import SemanticUnitDraft
    from arbiter.structuring.llm_extraction import LLMExtractionWrapper

    class WrongSchemaProvider:
        def structured_output(self, **_: object) -> SemanticUnitDraft:
            return SemanticUnitDraft(summary="wrong schema instance")

    wrapper = LLMExtractionWrapper(WrongSchemaProvider())
    result = wrapper._call_or_find(
        DocumentClassificationDraft,
        "Classify this document",
        {},
        "classification",
    )

    assert result is None
    assert any(f.code == "llm_schema_validation_failure" for f in wrapper.findings)
