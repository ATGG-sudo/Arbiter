from __future__ import annotations

from arbiter.schemas.regulation_structuring import NormalizedTextInput, ValidationSeverity
from arbiter.structuring.pipeline import structure_regulation


def test_duplicate_article_numbers_flagged() -> None:
    text = "Article 1\nFirst.\n\nArticle 1\nDuplicate."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    assert any(
        f.code == "duplicate_article_number" and f.severity is ValidationSeverity.WARNING
        for f in output.validation_report.findings
    )


def test_validation_findings_identify_stage_and_target_type() -> None:
    text = "Article 1\nFirst.\n\nArticle 1\nDuplicate."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    duplicate = next(
        f for f in output.validation_report.findings
        if f.code == "duplicate_article_number"
    )
    assert duplicate.stage == "unit"
    assert duplicate.target_type == "unit"

    temporal = next(
        f for f in output.validation_report.findings
        if f.code == "missing_temporal_metadata"
    )
    assert temporal.stage == "document"
    assert temporal.target_type == "document"


def test_invalid_tree_links_flagged() -> None:
    # This is hard to trigger through the deterministic splitter because it
    # only creates valid parent IDs. We test the validation function directly
    # via the report builder by constructing a scenario with a bad parent.
    from arbiter.schemas.regulation_structuring import (
        HierarchyPath,
        RegulationDocumentDraft,
        RegulationUnitDraft,
        SemanticUnitDraft,
        SourceLocation,
        StructuringValidationReport,
        TemporalMetadata,
        DocumentClassificationDraft,
        DocumentSourceType,
        DocumentStatus,
        ParseStatus,
    )
    from arbiter.structuring.validation import check_invalid_tree_links

    doc = RegulationDocumentDraft(
        document_id="doc-1",
        source_id="s1",
        source_file="f.txt",
        classification=DocumentClassificationDraft(
            source_type=DocumentSourceType.UNKNOWN,
        ),
        document_status=DocumentStatus.UNKNOWN,
        temporal_metadata=TemporalMetadata(),
        parse_status=ParseStatus.NEEDS_REVIEW,
    )
    units = [
        RegulationUnitDraft(
            unit_id="u1",
            document_id="doc-1",
            order_index=0,
            source_id="s1",
            source_file="f.txt",
            source_location=SourceLocation(),
            hierarchy=HierarchyPath(),
            original_text="text",
            semantic_draft=SemanticUnitDraft(),
            parent_unit_id="nonexistent",
        ),
    ]
    findings = check_invalid_tree_links("doc-1", units)
    assert any(f.code == "invalid_parent_unit_id" for f in findings)


def test_missing_provenance_flagged() -> None:
    from arbiter.schemas.regulation_structuring import (
        HierarchyPath,
        RegulationDocumentDraft,
        RegulationUnitDraft,
        SemanticUnitDraft,
        SourceLocation,
        DocumentClassificationDraft,
        DocumentSourceType,
        DocumentStatus,
        ParseStatus,
        TemporalMetadata,
    )
    from arbiter.structuring.validation import check_missing_provenance

    doc = RegulationDocumentDraft(
        document_id="doc-1",
        source_id="s1",
        source_file="f.txt",
        classification=DocumentClassificationDraft(
            source_type=DocumentSourceType.UNKNOWN,
        ),
        document_status=DocumentStatus.UNKNOWN,
        temporal_metadata=TemporalMetadata(),
        parse_status=ParseStatus.NEEDS_REVIEW,
    )
    units = [
        RegulationUnitDraft(
            unit_id="u1",
            document_id="doc-1",
            order_index=0,
            source_id="",
            source_file="",
            source_location=SourceLocation(),
            hierarchy=HierarchyPath(),
            original_text="text",
            semantic_draft=SemanticUnitDraft(),
        ),
    ]
    findings = check_missing_provenance("doc-1", units)
    assert any(f.code == "missing_source_provenance" for f in findings)


def test_ambiguous_references_create_ambiguous_edges() -> None:
    text = "Article 1\nSee Article 99."
    inp = NormalizedTextInput(source_id="t", source_file="t.txt", content_type="normalized_text", text=text)
    output = structure_regulation(inp)

    # Article 99 is not in the document, so the edge is ambiguous/unresolved
    edge = output.dependency_graph.dependency_edges[0]
    assert edge.resolution_status in {"unresolved", "ambiguous"}
    assert edge.to_unit_id is None
    assert edge.ambiguity_notes
