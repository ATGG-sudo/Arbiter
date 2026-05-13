from __future__ import annotations

import pytest
from pydantic import ValidationError

from arbiter.schemas.regulation_structuring import (
    DocumentClassificationDraft,
    DocumentSourceType,
    ReviewStatus,
)


def test_mock_model_provider_validates_structured_output(mock_model_provider) -> None:
    result = mock_model_provider.structured_output(
        schema=DocumentClassificationDraft,
        payload={
            "source_type": "external_regulation",
            "issuer_type": "government_regulator",
            "issuer_name": "Regulator",
            "categories": [],
            "topic_tags": ["disclosure"],
            "classification_tags": [],
            "evidence_text": ["Regulator notice"],
            "confidence": 0.8,
            "ambiguity_notes": [],
        },
    )

    assert result.source_type is DocumentSourceType.EXTERNAL_REGULATION
    assert result.review_status is ReviewStatus.NEEDS_REVIEW
    assert mock_model_provider.calls[0]["schema"] is DocumentClassificationDraft


def test_mock_model_provider_rejects_schema_invalid_output(mock_model_provider) -> None:
    with pytest.raises(ValidationError):
        mock_model_provider.structured_output(
            schema=DocumentClassificationDraft,
            payload={
                "source_type": "not-a-valid-source-type",
                "issuer_type": "government_regulator",
                "issuer_name": "Regulator",
                "categories": [],
                "topic_tags": [],
                "classification_tags": [],
                "evidence_text": [],
                "ambiguity_notes": [],
            },
        )


def test_blocking_provider_prevents_real_model_calls(blocking_model_provider) -> None:
    with pytest.raises(AssertionError, match="Real model calls are forbidden"):
        blocking_model_provider.structured_output(schema=DocumentClassificationDraft, payload={})
