from __future__ import annotations

from collections import Counter
from typing import Any

from arbiter.schemas.regulation_structuring import (
    DependencyEdgeDraft,
    HierarchyPath,
    ReferenceCandidate,
    RegulationDocumentDraft,
    RegulationUnitDraft,
    ResolvedDependencyGraphDraft,
    SourceLocation,
    SourceLocationKind,
    StructuringValidationFinding,
    StructuringValidationReport,
    TemporalMetadata,
    ValidationSeverity,
)


def _finding(
    code: str,
    severity: ValidationSeverity,
    message: str,
    *,
    stage: str = "output",
    target_type: str = "unknown",
    target_id: str | None = None,
    document_id: str | None = None,
    unit_id: str | None = None,
    source_location: SourceLocation | None = None,
) -> StructuringValidationFinding:
    return StructuringValidationFinding(
        stage=stage,
        target_type=target_type,
        target_id=target_id,
        code=code,
        severity=severity,
        message=message,
        document_id=document_id,
        unit_id=unit_id,
        source_location=source_location,
    )


def check_duplicate_article_numbers(
    document_id: str,
    units: list[RegulationUnitDraft],
) -> list[StructuringValidationFinding]:
    findings: list[StructuringValidationFinding] = []
    counts: Counter[str | None] = Counter()
    for unit in units:
        counts[unit.hierarchy.article_number] += 1
    for article_number, count in counts.items():
        if article_number is not None and count > 1:
            findings.append(
                _finding(
                    "duplicate_article_number",
                    ValidationSeverity.WARNING,
                    f"Article number '{article_number}' appears {count} times",
                    stage="unit",
                    target_type="unit",
                    document_id=document_id,
                )
            )
    return findings


def check_invalid_tree_links(
    document_id: str,
    units: list[RegulationUnitDraft],
) -> list[StructuringValidationFinding]:
    findings: list[StructuringValidationFinding] = []
    unit_ids = {u.unit_id for u in units}
    for unit in units:
        if unit.parent_unit_id is not None and unit.parent_unit_id not in unit_ids:
            findings.append(
                _finding(
                    "invalid_parent_unit_id",
                    ValidationSeverity.ERROR,
                    f"Unit {unit.unit_id} references unknown parent {unit.parent_unit_id}",
                    stage="unit",
                    target_type="unit",
                    target_id=unit.unit_id,
                    document_id=document_id,
                    unit_id=unit.unit_id,
                )
            )
    return findings


def check_missing_provenance(
    document_id: str,
    units: list[RegulationUnitDraft],
) -> list[StructuringValidationFinding]:
    findings: list[StructuringValidationFinding] = []
    for unit in units:
        if not unit.source_id or not unit.source_file:
            findings.append(
                _finding(
                    "missing_source_provenance",
                    ValidationSeverity.WARNING,
                    f"Unit {unit.unit_id} is missing source_id or source_file",
                    stage="unit",
                    target_type="unit",
                    target_id=unit.unit_id,
                    document_id=document_id,
                    unit_id=unit.unit_id,
                )
            )
    return findings


def check_temporal_ambiguity(
    document: RegulationDocumentDraft,
) -> list[StructuringValidationFinding]:
    findings: list[StructuringValidationFinding] = []
    if (
        document.effective_date is None
        and document.promulgation_date is None
        and document.repeal_date is None
        and not document.temporal_metadata.ambiguity_notes
    ):
        findings.append(
            _finding(
                "missing_temporal_metadata",
                ValidationSeverity.INFO,
                "No temporal dates were extracted from the document",
                stage="document",
                target_type="document",
                target_id=document.document_id,
                document_id=document.document_id,
            )
        )
    return findings


def check_reference_ambiguity(
    document_id: str,
    reference_candidates: list[ReferenceCandidate],
) -> list[StructuringValidationFinding]:
    findings: list[StructuringValidationFinding] = []
    for candidate in reference_candidates:
        if candidate.confidence is not None and candidate.confidence < 0.5:
            findings.append(
                _finding(
                    "low_confidence_reference",
                    ValidationSeverity.WARNING,
                    f"Reference candidate {candidate.candidate_id} has low confidence",
                    stage="reference",
                    target_type="reference_candidate",
                    target_id=candidate.candidate_id,
                    document_id=document_id,
                    unit_id=candidate.from_unit_id,
                )
            )
    return findings


def check_dependency_graph_issues(
    document_id: str,
    graph: ResolvedDependencyGraphDraft,
) -> list[StructuringValidationFinding]:
    findings: list[StructuringValidationFinding] = []
    for edge in graph.dependency_edges:
        if edge.resolution_status in {"unresolved", "ambiguous"} and not edge.ambiguity_notes:
            findings.append(
                _finding(
                    "ambiguous_dependency_without_notes",
                    ValidationSeverity.WARNING,
                    f"Edge {edge.edge_id} is unresolved/ambiguous but has no ambiguity notes",
                    stage="dependency",
                    target_type="dependency_edge",
                    target_id=edge.edge_id,
                    document_id=document_id,
                    unit_id=edge.from_unit_id,
                )
            )
    return findings


def build_validation_report(
    document: RegulationDocumentDraft,
    units: list[RegulationUnitDraft],
    reference_candidates: list[ReferenceCandidate],
    dependency_graph: ResolvedDependencyGraphDraft,
    intake_findings: list[StructuringValidationFinding] | None = None,
    extraction_findings: list[StructuringValidationFinding] | None = None,
) -> StructuringValidationReport:
    """Assemble a validation report from all pipeline stages."""
    findings: list[StructuringValidationFinding] = []
    findings.extend(intake_findings or [])
    findings.extend(extraction_findings or [])
    findings.extend(check_duplicate_article_numbers(document.document_id, units))
    findings.extend(check_invalid_tree_links(document.document_id, units))
    findings.extend(check_missing_provenance(document.document_id, units))
    findings.extend(check_temporal_ambiguity(document))
    findings.extend(check_reference_ambiguity(document.document_id, reference_candidates))
    findings.extend(check_dependency_graph_issues(document.document_id, dependency_graph))

    error_count = sum(1 for f in findings if f.severity is ValidationSeverity.ERROR)
    warning_count = sum(1 for f in findings if f.severity is ValidationSeverity.WARNING)
    info_count = sum(1 for f in findings if f.severity is ValidationSeverity.INFO)

    summary_parts = [f"Validation completed with {len(findings)} finding(s)"]
    if error_count:
        summary_parts.append(f"{error_count} error(s)")
    if warning_count:
        summary_parts.append(f"{warning_count} warning(s)")
    if info_count:
        summary_parts.append(f"{info_count} info")
    if len(summary_parts) == 1:
        summary_parts.append("no issues detected")
    summary = " — ".join(summary_parts)

    return StructuringValidationReport(
        document_id=document.document_id,
        summary=summary,
        findings=findings,
    )
