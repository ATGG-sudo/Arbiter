from __future__ import annotations

from typing import Any

from arbiter.schemas.regulation_structuring import (
    ExtractionMethod,
    ExtractionProvenance,
    NormalizedTextInput,
    StructuringPipelineOutput,
    StructuringValidationFinding,
)
from arbiter.structuring.extraction import (
    build_dependency_graph,
    build_document_draft,
    build_regulation_units,
    extract_reference_candidates,
    split_text,
)
from arbiter.structuring.intake import validate_normalized_input
from arbiter.structuring.llm_extraction import LLMExtractionWrapper
from arbiter.structuring.validation import build_validation_report


def structure_regulation(
    input: NormalizedTextInput,
    model_provider: Any | None = None,
) -> StructuringPipelineOutput:
    """Run the offline regulation structuring pipeline.

    Returns a draft-only output bundle containing a document draft, unit drafts,
    reference candidates, a dependency graph draft, and a validation report.
    No runtime-safe assets, JudgmentResult, RuleItem, RulePack, or final
    compliance conclusions are produced.
    """
    # Intake validation
    intake_findings = validate_normalized_input(input)
    if any(f.severity.value == "error" for f in intake_findings):
        # Build minimal output with only the validation report for fatal errors
        document = build_document_draft(input)
        report = build_validation_report(
            document=document,
            units=[],
            reference_candidates=[],
            dependency_graph=build_dependency_graph(document.document_id, [], []),
            intake_findings=intake_findings,
        )
        return StructuringPipelineOutput(
            extraction_provenance=ExtractionProvenance(
                extraction_method=ExtractionMethod.DETERMINISTIC,
                prompt_contract_version=None,
                model_trace_id=None,
            ),
            document=document,
            units=[],
            reference_candidates=[],
            dependency_graph=build_dependency_graph(document.document_id, [], []),
            validation_report=report,
        )

    # Deterministic extraction
    document = build_document_draft(input)
    document_id = document.document_id
    candidates, extraction_findings = split_text(input)
    units = build_regulation_units(
        candidates,
        document_id=document_id,
        source_id=input.source_id,
        source_file=input.source_file,
    )

    # Reference and dependency graph (deterministic)
    ref_candidates = extract_reference_candidates(units, document_id)
    dep_graph = build_dependency_graph(document_id, ref_candidates, units)

    # Optional LLM-assisted enrichment
    llm_findings: list[StructuringValidationFinding] = []
    extraction_method = ExtractionMethod.DETERMINISTIC
    prompt_contract_version: str | None = None
    model_trace_id: str | None = None

    if model_provider is not None:
        wrapper = LLMExtractionWrapper(model_provider)

        enriched = wrapper.enrich_classification(
            document.classification,
            document_title=document.title,
            document_text=input.text,
        )
        if enriched is not None:
            document.classification = enriched

        for unit in units:
            wrapper.enrich_semantic_draft(unit)

        llm_edges = wrapper.propose_dependency_edges(
            document_id=document_id,
            reference_candidates=ref_candidates,
            units=units,
        )
        if llm_edges:
            dep_graph.dependency_edges.extend(llm_edges)

        if wrapper.validated_call_count > 0:
            extraction_method = ExtractionMethod.MIXED
            prompt_contract_version = "structuring-v1"
            model_trace_id = "trace-llm"

        llm_findings.extend(wrapper.findings)

    # Validation report
    validation_report = build_validation_report(
        document=document,
        units=units,
        reference_candidates=ref_candidates,
        dependency_graph=dep_graph,
        intake_findings=intake_findings,
        extraction_findings=extraction_findings + llm_findings,
    )

    return StructuringPipelineOutput(
        extraction_provenance=ExtractionProvenance(
            extraction_method=extraction_method,
            prompt_contract_version=prompt_contract_version,
            model_trace_id=model_trace_id,
        ),
        document=document,
        units=units,
        reference_candidates=ref_candidates,
        dependency_graph=dep_graph,
        validation_report=validation_report,
    )
