from __future__ import annotations

from arbiter.schemas.regulation_structuring import (
    NormalizedTextInput,
    ReviewStatus,
)
from arbiter.structuring.pipeline import structure_regulation


def test_all_document_outputs_have_needs_review_status() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    assert output.document.classification.review_status is ReviewStatus.NEEDS_REVIEW
    assert output.document.parse_status.value == "needs_review"


def test_all_unit_outputs_have_needs_review_status() -> None:
    text = "Article 1\nContent.\n\nArticle 2\nMore."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    for unit in output.units:
        assert unit.review_status is ReviewStatus.NEEDS_REVIEW
        assert unit.semantic_draft.review_status is ReviewStatus.NEEDS_REVIEW


def test_all_dependency_edges_have_needs_review_status() -> None:
    text = "Article 1\nSee Article 2.\n\nArticle 2\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    for edge in output.dependency_graph.dependency_edges:
        assert edge.review_status is ReviewStatus.NEEDS_REVIEW


def test_pipeline_never_assigns_approved_rejected_or_superseded() -> None:
    text = "Article 1\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    forbidden = {ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.SUPERSEDED}
    assert output.document.classification.review_status not in forbidden
    for unit in output.units:
        assert unit.review_status not in forbidden
        assert unit.semantic_draft.review_status not in forbidden
    for edge in output.dependency_graph.dependency_edges:
        assert edge.review_status not in forbidden
