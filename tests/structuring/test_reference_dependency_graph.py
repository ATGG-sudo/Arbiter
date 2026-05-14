from __future__ import annotations

from arbiter.schemas.regulation_structuring import (
    DocumentSourceType,
    NormalizedTextInput,
    ReviewStatus,
)
from arbiter.structuring.pipeline import structure_regulation


def test_reference_candidates_are_separate_from_dependency_edges() -> None:
    text = "Article 1\nSee Article 2.\n\nArticle 2\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    assert len(output.reference_candidates) > 0
    assert len(output.dependency_graph.dependency_edges) > 0
    # Candidates live at top level; graph references them by ID
    candidate_ids = {c.candidate_id for c in output.reference_candidates}
    for edge in output.dependency_graph.dependency_edges:
        for cid in edge.source_candidate_ids:
            assert cid in candidate_ids


def test_cross_document_links_remain_ambiguous() -> None:
    text = "Article 1\nSee External Reporting Rules."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    edges = output.dependency_graph.dependency_edges
    assert len(edges) >= 1
    edge = edges[0]
    assert edge.resolution_status in {"unresolved", "ambiguous"}
    assert edge.to_unit_id is None
    assert edge.review_status is ReviewStatus.NEEDS_REVIEW


def test_no_reviewed_dependency_edge_produced() -> None:
    text = "Article 1\nSee Article 2.\n\nArticle 2\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    raw = output.model_dump_json()
    assert "ReviewedDependencyEdge" not in raw


def test_external_document_target_metadata_preserved() -> None:
    text = "Article 1\nSee External Reporting Rules."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    edge = output.dependency_graph.dependency_edges[0]
    assert edge.target_label is not None
    assert "External" in edge.target_label


def test_external_english_title_gets_external_document_scope() -> None:
    text = "Article 1\nSee External Reporting Rules."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    edge = next(
        e for e in output.dependency_graph.dependency_edges
        if e.target_label and "External" in e.target_label
    )
    assert edge.target_scope == "external_document"
    assert edge.target_document_title == "External Reporting Rules"
    assert edge.target_source_type is DocumentSourceType.EXTERNAL_REGULATION
    assert edge.resolution_status == "ambiguous"
    assert edge.to_unit_id is None
    assert edge.review_status is ReviewStatus.NEEDS_REVIEW


def test_external_chinese_title_gets_external_document_scope() -> None:
    text = "第一条\n参见《信息披露管理办法》及《外部报告规则》。"
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    edges = [
        e for e in output.dependency_graph.dependency_edges
        if e.target_scope == "external_document"
    ]
    assert len(edges) >= 2
    titles = {e.target_document_title for e in edges}
    assert "信息披露管理办法" in titles
    assert "外部报告规则" in titles
    for edge in edges:
        assert edge.resolution_status == "ambiguous"
        assert edge.to_unit_id is None
        assert edge.review_status is ReviewStatus.NEEDS_REVIEW


def test_same_document_article_still_resolved() -> None:
    text = "Article 1\nSee Article 2.\n\nArticle 2\nContent."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    edge = next(
        e for e in output.dependency_graph.dependency_edges
        if e.target_label and "Article 2" in e.target_label
    )
    assert edge.target_scope == "same_document"
    assert edge.resolution_status == "resolved"
    assert edge.to_unit_id is not None
    assert edge.review_status is ReviewStatus.NEEDS_REVIEW
