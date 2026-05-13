from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from arbiter.schemas.regulation_structuring import (
    DependencyEdgeDraft,
    DocumentCategory,
    DocumentClassificationDraft,
    DocumentSourceType,
    DocumentStatus,
    ExtractionMethod,
    ExtractionProvenance,
    FileInput,
    HierarchyPath,
    NormalizedTextInput,
    ParseStatus,
    ReferenceCandidate,
    RegulationDocumentDraft,
    RegulationUnitDraft,
    RegulationUnitRelationDraft,
    RelationKind,
    ResolvedDependencyGraphDraft,
    ReviewStatus,
    SemanticUnitDraft,
    SourceLocation,
    SourceLocationKind,
    StructuringPipelineOutput,
    StructuringValidationFinding,
    StructuringValidationReport,
    TemporalMetadata,
    ValidationSeverity,
)


def classification() -> DocumentClassificationDraft:
    return DocumentClassificationDraft(
        source_type=DocumentSourceType.INTERNAL_POLICY,
        issuer_type="internal_org",
        issuer_name="Risk Department",
        categories=[
            DocumentCategory(
                category_code=None,
                category_label="Investment",
                tags=["investment"],
                evidence_text="Internal Policy",
                confidence=0.8,
                ambiguity_notes=[],
            )
        ],
        topic_tags=["investment"],
        classification_tags=[],
        evidence_text=["Internal Policy"],
        confidence=0.8,
        ambiguity_notes=[],
    )


def source_location() -> SourceLocation:
    return SourceLocation(
        kind=SourceLocationKind.PARAGRAPH_INDEX,
        value="1",
        confidence="explicit",
    )


def semantic_draft() -> SemanticUnitDraft:
    return SemanticUnitDraft(
        unit_type="obligation",
        normalized_title="Reporting",
        definitions=[],
        obligations=["report material changes"],
        exceptions=[],
        applicability=["investment activity"],
        actors=["manager"],
        conditions=[],
        trigger_events=["material change"],
        required_actions=["report"],
        prohibited_actions=[],
        deadlines=["3 working days"],
        thresholds=[],
        subject_scope=["manager"],
        object_scope=["investment activity"],
        reporting_obligations=["report material changes"],
        evidence_text=["must report material changes within 3 working days"],
        confidence=0.9,
        ambiguity_notes=[],
    )


def document() -> RegulationDocumentDraft:
    return RegulationDocumentDraft(
        document_id="doc-1",
        source_id="source-1",
        source_file="policy.md",
        classification=classification(),
        title="Internal Policy",
        document_status=DocumentStatus.OFFICIAL,
        effective_date=date(2026, 1, 1),
        promulgation_date=None,
        repeal_date=None,
        temporal_metadata=TemporalMetadata(
            version_label="v1",
            amendment_history_text=None,
            validity_notes=[],
            temporal_confidence=0.7,
            ambiguity_notes=[],
        ),
        warnings=[],
    )


def unit() -> RegulationUnitDraft:
    return RegulationUnitDraft(
        unit_id="unit-1",
        document_id="doc-1",
        parent_unit_id=None,
        order_index=0,
        display_label="Article 1",
        source_id="source-1",
        source_file="policy.md",
        source_location=source_location(),
        hierarchy=HierarchyPath(
            chapter=None,
            section=None,
            article_number="Article 1",
            article_title="Reporting",
            paragraph_index=1,
            item_label=None,
        ),
        original_text="The manager must report material changes within 3 working days.",
        normalized_text="The manager must report material changes within 3 working days.",
        semantic_draft=semantic_draft(),
        warnings=[],
    )


def test_enums_include_reserved_review_status_values() -> None:
    assert ReviewStatus.NEEDS_REVIEW.value == "needs_review"
    assert ReviewStatus.APPROVED.value == "approved"
    assert ReviewStatus.REJECTED.value == "rejected"
    assert ReviewStatus.SUPERSEDED.value == "superseded"
    assert ParseStatus.NEEDS_REVIEW.value == "needs_review"
    assert ValidationSeverity.WARNING.value == "warning"


def test_schema_defaults_keep_drafts_needs_review() -> None:
    assert document().parse_status is ParseStatus.NEEDS_REVIEW
    assert classification().review_status is ReviewStatus.NEEDS_REVIEW
    assert semantic_draft().review_status is ReviewStatus.NEEDS_REVIEW
    assert unit().review_status is ReviewStatus.NEEDS_REVIEW


def test_direct_input_and_optional_file_boundary_models() -> None:
    file_input = FileInput(
        source_id="source-1",
        source_file="policy.docx",
        file_type="docx",
        file_ref="opaque-ref",
    )
    normalized = NormalizedTextInput(
        source_id=file_input.source_id,
        source_file="policy.md",
        content_type="markdown",
        text="# Policy",
        source_type=DocumentSourceType.INTERNAL_POLICY,
    )

    assert normalized.source_id == "source-1"
    assert normalized.content_type == "markdown"


def test_forbids_extra_fields_and_empty_text() -> None:
    with pytest.raises(ValidationError):
        NormalizedTextInput(
            source_id="source-1",
            source_file="policy.md",
            content_type="markdown",
            text="   ",
        )

    with pytest.raises(ValidationError):
        RegulationDocumentDraft(
            **document().model_dump(),
            unexpected="not allowed",
        )


def test_reference_candidate_dependency_edge_and_alias() -> None:
    candidate = ReferenceCandidate(
        candidate_id="candidate-1",
        document_id="doc-1",
        from_unit_id="unit-1",
        target_label="Article 2",
        evidence_text="See Article 2",
        source_location=source_location(),
        confidence=0.6,
        ambiguity_notes=["target article needs review"],
        warnings=[],
    )
    edge = DependencyEdgeDraft(
        edge_id="edge-1",
        document_id="doc-1",
        from_unit_id="unit-1",
        to_unit_id=None,
        target_document_id=None,
        target_document_title=None,
        target_source_type=None,
        target_label="Article 2",
        target_scope="unknown",
        resolution_status="ambiguous",
        relation_kind=RelationKind.CROSS_REFERENCE,
        source_candidate_ids=[candidate.candidate_id],
        evidence_text="See Article 2",
        confidence=0.6,
        ambiguity_notes=["target article needs review"],
    )

    assert RegulationUnitRelationDraft is DependencyEdgeDraft
    assert edge.review_status is ReviewStatus.NEEDS_REVIEW


def test_validation_report_and_output_bundle_models() -> None:
    candidate = ReferenceCandidate(
        candidate_id="candidate-1",
        document_id="doc-1",
        from_unit_id="unit-1",
        target_label="Article 2",
        evidence_text="See Article 2",
        source_location=source_location(),
        confidence=0.6,
        ambiguity_notes=[],
        warnings=[],
    )
    graph = ResolvedDependencyGraphDraft(
        graph_id="graph-1",
        document_id="doc-1",
        reference_candidate_ids=[candidate.candidate_id],
        dependency_edges=[],
        warnings=[],
    )
    report = StructuringValidationReport(
        document_id="doc-1",
        summary="Review required",
        findings=[
            StructuringValidationFinding(
                code="ambiguous_reference",
                severity=ValidationSeverity.WARNING,
                message="Reference target needs review",
                document_id="doc-1",
                unit_id="unit-1",
                source_location=source_location(),
            )
        ],
    )
    output = StructuringPipelineOutput(
        extraction_provenance=ExtractionProvenance(
            extraction_method=ExtractionMethod.MIXED,
            prompt_contract_version="structuring-v1",
            model_trace_id="trace-1",
        ),
        document=document(),
        units=[unit()],
        reference_candidates=[candidate],
        dependency_graph=graph,
        validation_report=report,
    )

    assert output.contract_version == "v1"
    assert output.validation_report.has_errors is False
