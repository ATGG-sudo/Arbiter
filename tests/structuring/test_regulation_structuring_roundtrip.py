from __future__ import annotations

from arbiter.schemas.regulation_structuring import (
    DependencyEdgeDraft,
    DocumentClassificationDraft,
    DocumentSourceType,
    ExtractionMethod,
    ExtractionProvenance,
    HierarchyPath,
    ReferenceCandidate,
    RegulationDocumentDraft,
    RegulationUnitDraft,
    RelationKind,
    ResolvedDependencyGraphDraft,
    SemanticUnitDraft,
    SourceLocation,
    SourceLocationKind,
    StructuringPipelineOutput,
    StructuringValidationReport,
    TemporalMetadata,
)
from arbiter.structuring.export import UnsafeExportError, from_json, to_json


def output_bundle(**overrides: object) -> StructuringPipelineOutput:
    location = SourceLocation(kind=SourceLocationKind.PARAGRAPH_INDEX, value="1")
    semantic = SemanticUnitDraft(
        definitions=[],
        obligations=["report"],
        exceptions=[],
        applicability=[],
        actors=["manager"],
        conditions=[],
        trigger_events=[],
        required_actions=["report"],
        prohibited_actions=[],
        deadlines=["3 days"],
        thresholds=[],
        subject_scope=["manager"],
        object_scope=[],
        reporting_obligations=["report"],
        evidence_text=["must report"],
        ambiguity_notes=[],
    )
    document = RegulationDocumentDraft(
        document_id="doc-1",
        source_id="source-1",
        source_file="policy.md",
        classification=DocumentClassificationDraft(
            source_type=DocumentSourceType.INTERNAL_POLICY,
            issuer_type="internal_org",
            issuer_name="Risk",
            categories=[],
            topic_tags=[],
            classification_tags=[],
            evidence_text=["Internal Policy"],
            ambiguity_notes=[],
        ),
        title="Policy",
        temporal_metadata=TemporalMetadata(validity_notes=[], ambiguity_notes=[]),
        warnings=[],
    )
    unit = RegulationUnitDraft(
        unit_id="unit-1",
        document_id="doc-1",
        parent_unit_id=None,
        order_index=0,
        display_label="Article 1",
        source_id="source-1",
        source_file="policy.md",
        source_location=location,
        hierarchy=HierarchyPath(article_number="Article 1"),
        original_text="The manager must report.",
        normalized_text="The manager must report.",
        semantic_draft=semantic,
        warnings=[],
    )
    candidate = ReferenceCandidate(
        candidate_id="candidate-1",
        document_id="doc-1",
        from_unit_id="unit-1",
        target_label="External Reporting Rules",
        evidence_text="See External Reporting Rules",
        source_location=location,
        ambiguity_notes=[],
        warnings=[],
    )
    edge = DependencyEdgeDraft(
        edge_id="edge-1",
        document_id="doc-1",
        from_unit_id="unit-1",
        to_unit_id=None,
        target_document_id=None,
        target_document_title="External Reporting Rules",
        target_source_type=DocumentSourceType.EXTERNAL_REGULATION,
        target_label="External Reporting Rules",
        target_scope="external_document",
        resolution_status="ambiguous",
        relation_kind=RelationKind.CROSS_REFERENCE,
        source_candidate_ids=["candidate-1"],
        evidence_text="See External Reporting Rules",
        ambiguity_notes=["external target is unresolved"],
    )
    data = {
        "extraction_provenance": ExtractionProvenance(
            extraction_method=ExtractionMethod.MIXED,
            prompt_contract_version="structuring-v1",
            model_trace_id="trace-1",
        ),
        "document": document,
        "units": [unit],
        "reference_candidates": [candidate],
        "dependency_graph": ResolvedDependencyGraphDraft(
            graph_id="graph-1",
            document_id="doc-1",
            reference_candidate_ids=["candidate-1"],
            dependency_edges=[edge],
            warnings=[],
        ),
        "validation_report": StructuringValidationReport(
            document_id="doc-1",
            summary="Review required",
            findings=[],
        ),
    }
    data.update(overrides)
    return StructuringPipelineOutput(**data)


def test_output_round_trips_without_losing_review_surface() -> None:
    raw = to_json(output_bundle())
    restored = from_json(raw)

    assert restored.document.document_id == "doc-1"
    assert restored.document.source_id == "source-1"
    assert restored.units[0].original_text == "The manager must report."
    assert restored.extraction_provenance.prompt_contract_version == "structuring-v1"
    assert restored.dependency_graph.dependency_edges[0].target_document_title == "External Reporting Rules"


def test_export_rejects_secrets_prompts_payloads_paths_and_raw_sensitive_text() -> None:
    unsafe_cases = [
        {"extraction_provenance": ExtractionProvenance(extraction_method=ExtractionMethod.MIXED, model_trace_id="sk-test-secret")},
        {"extraction_provenance": ExtractionProvenance(extraction_method=ExtractionMethod.MIXED, prompt_contract_version="full prompt: extract everything")},
        {"extraction_provenance": ExtractionProvenance(extraction_method=ExtractionMethod.MIXED, model_trace_id='{"choices": []}')},
        {"document": output_bundle().document.model_copy(update={"source_file": "/mnt/e/private/policy.md"})},
        {"validation_report": StructuringValidationReport(document_id="doc-1", summary="RAW_SENSITIVE_TEXT: customer fact", findings=[])},
    ]

    for override in unsafe_cases:
        try:
            bundle = output_bundle(**override)
        except ValueError:
            continue
        try:
            to_json(bundle)
        except UnsafeExportError:
            continue
        raise AssertionError(f"unsafe export was accepted: {override}")
