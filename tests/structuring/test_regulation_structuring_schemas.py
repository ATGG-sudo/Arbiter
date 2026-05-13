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
        confidence=1.0,
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


def dependency_edge(**overrides: object) -> DependencyEdgeDraft:
    data: dict[str, object] = {
        "edge_id": "edge-1",
        "document_id": "doc-1",
        "from_unit_id": "unit-1",
        "to_unit_id": None,
        "target_document_id": None,
        "target_document_title": None,
        "target_source_type": None,
        "target_label": "Article 2",
        "target_scope": "unknown",
        "resolution_status": "ambiguous",
        "relation_kind": RelationKind.CROSS_REFERENCE,
        "source_candidate_ids": [],
        "evidence_text": "See Article 2",
        "confidence": 0.6,
        "ambiguity_notes": ["target article needs review"],
    }
    data.update(overrides)
    return DependencyEdgeDraft(**data)


def reference_candidate(**overrides: object) -> ReferenceCandidate:
    data: dict[str, object] = {
        "candidate_id": "candidate-1",
        "document_id": "doc-1",
        "from_unit_id": "unit-1",
        "target_label": "Article 2",
        "evidence_text": "See Article 2",
        "source_location": source_location(),
        "confidence": 0.6,
        "ambiguity_notes": [],
        "warnings": [],
    }
    data.update(overrides)
    return ReferenceCandidate(**data)


def validation_report(**overrides: object) -> StructuringValidationReport:
    data: dict[str, object] = {
        "document_id": "doc-1",
        "summary": "Review required",
        "findings": [],
    }
    data.update(overrides)
    return StructuringValidationReport(**data)


def dependency_graph(**overrides: object) -> ResolvedDependencyGraphDraft:
    data: dict[str, object] = {
        "graph_id": "graph-1",
        "document_id": "doc-1",
        "reference_candidate_ids": ["candidate-1"],
        "dependency_edges": [],
        "warnings": [],
    }
    data.update(overrides)
    return ResolvedDependencyGraphDraft(**data)


def pipeline_output(**overrides: object) -> StructuringPipelineOutput:
    data: dict[str, object] = {
        "extraction_provenance": ExtractionProvenance(
            extraction_method=ExtractionMethod.MIXED,
            prompt_contract_version="structuring-v1",
            model_trace_id="trace-1",
        ),
        "document": document(),
        "units": [unit()],
        "reference_candidates": [reference_candidate()],
        "dependency_graph": dependency_graph(),
        "validation_report": validation_report(),
    }
    data.update(overrides)
    return StructuringPipelineOutput(**data)


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
    edge = dependency_edge(
        source_candidate_ids=[candidate.candidate_id],
    )

    assert RegulationUnitRelationDraft is DependencyEdgeDraft
    assert edge.review_status is ReviewStatus.NEEDS_REVIEW


def test_dependency_edge_requires_to_unit_for_resolved_same_document() -> None:
    with pytest.raises(ValidationError):
        dependency_edge(
            target_scope="same_document",
            resolution_status="resolved",
            to_unit_id=None,
        )


def test_dependency_edge_accepts_to_unit_for_resolved_same_document() -> None:
    edge = dependency_edge(
        target_scope="same_document",
        resolution_status="resolved",
        to_unit_id="unit-2",
        target_label=None,
        ambiguity_notes=[],
    )

    assert edge.to_unit_id == "unit-2"


def test_dependency_edge_requires_target_for_resolved_external_document() -> None:
    with pytest.raises(ValidationError):
        dependency_edge(
            target_scope="external_document",
            resolution_status="resolved",
            target_document_id=None,
            target_document_title=None,
            target_label=None,
            ambiguity_notes=[],
        )


def test_dependency_edge_requires_label_or_notes_for_unresolved() -> None:
    with pytest.raises(ValidationError):
        dependency_edge(
            resolution_status="unresolved",
            target_label=None,
            ambiguity_notes=[],
        )


def test_dependency_edge_accepts_ambiguity_notes_for_ambiguous() -> None:
    edge = dependency_edge(
        resolution_status="ambiguous",
        target_label=None,
        ambiguity_notes=["candidate target cannot be resolved from provided text"],
    )

    assert edge.resolution_status == "ambiguous"


def test_validation_report_and_output_bundle_models() -> None:
    output = pipeline_output(
        validation_report=validation_report(
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
    )

    assert output.contract_version == "v1"
    assert output.validation_report.has_errors is False


def test_validation_finding_target_metadata_defaults_and_values() -> None:
    default_finding = StructuringValidationFinding(
        code="output_warning",
        severity=ValidationSeverity.WARNING,
        message="Output needs review",
    )
    dependency_finding = StructuringValidationFinding(
        stage="dependency",
        target_type="dependency_edge",
        target_id="edge-1",
        code="ambiguous_dependency",
        severity=ValidationSeverity.WARNING,
        message="Dependency target needs review",
    )

    assert default_finding.stage == "output"
    assert default_finding.target_type == "unknown"
    assert default_finding.target_id is None
    assert dependency_finding.stage == "dependency"
    assert dependency_finding.target_type == "dependency_edge"
    assert dependency_finding.target_id == "edge-1"


def test_validation_report_counts_findings_by_severity() -> None:
    report = validation_report(
        findings=[
            StructuringValidationFinding(
                code="schema_error",
                severity=ValidationSeverity.ERROR,
                message="Schema validation failed",
            ),
            StructuringValidationFinding(
                code="ambiguous_reference",
                severity=ValidationSeverity.WARNING,
                message="Reference target needs review",
            ),
            StructuringValidationFinding(
                code="normalized",
                severity=ValidationSeverity.INFO,
                message="Input normalized",
            ),
        ],
    )

    assert report.error_count == 1
    assert report.warning_count == 1
    assert report.info_count == 1
    assert report.has_errors is True


def test_validation_report_has_errors_false_without_error_findings() -> None:
    report = validation_report(
        findings=[
            StructuringValidationFinding(
                code="ambiguous_reference",
                severity=ValidationSeverity.WARNING,
                message="Reference target needs review",
            )
        ],
    )

    assert report.error_count == 0
    assert report.warning_count == 1
    assert report.info_count == 0
    assert report.has_errors is False


def test_pipeline_output_requires_matching_validation_report_document_id() -> None:
    with pytest.raises(ValidationError):
        pipeline_output(validation_report=validation_report(document_id="doc-other"))


def test_pipeline_output_requires_matching_dependency_graph_document_id() -> None:
    with pytest.raises(ValidationError):
        pipeline_output(dependency_graph=dependency_graph(document_id="doc-other"))


def test_pipeline_output_requires_matching_unit_document_ids() -> None:
    with pytest.raises(ValidationError):
        pipeline_output(units=[unit().model_copy(update={"document_id": "doc-other"})])


def test_pipeline_output_requires_matching_reference_candidate_document_ids() -> None:
    with pytest.raises(ValidationError):
        pipeline_output(
            reference_candidates=[
                reference_candidate(document_id="doc-other"),
            ]
        )


def test_pipeline_output_rejects_blank_contract_version() -> None:
    with pytest.raises(ValidationError):
        pipeline_output(contract_version=" ")
