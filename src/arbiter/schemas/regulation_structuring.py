from __future__ import annotations

import re
from datetime import date
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DocumentStatus(str, Enum):
    OFFICIAL = "official"
    DRAFT_FOR_COMMENT = "draft_for_comment"
    DEPRECATED = "deprecated"
    UNKNOWN = "unknown"


class ParseStatus(str, Enum):
    PARSED = "parsed"  # Structuring completed; draft still needs review.
    PARTIAL = "partial"  # Structuring partially completed.
    NEEDS_REVIEW = "needs_review"
    FAILED = "failed"


class ReviewStatus(str, Enum):
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class DocumentSourceType(str, Enum):
    EXTERNAL_REGULATION = "external_regulation"
    INTERNAL_POLICY = "internal_policy"
    UNKNOWN = "unknown"


class IssuerType(str, Enum):
    GOVERNMENT_REGULATOR = "government_regulator"
    SELF_REGULATORY_ORGANIZATION = "self_regulatory_organization"
    INTERNAL_ORG = "internal_org"
    EXTERNAL_OTHER = "external_other"
    JOINT_ISSUERS = "joint_issuers"
    UNKNOWN = "unknown"


class SourceLocationKind(str, Enum):
    PAGE_NUMBER = "page_number"
    LINE_NUMBER = "line_number"
    PARAGRAPH_INDEX = "paragraph_index"
    HEADING_PATH = "heading_path"
    UNKNOWN = "unknown"


class ValidationSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ExtractionMethod(str, Enum):
    DETERMINISTIC = "deterministic"
    LLM_ASSISTED = "llm_assisted"
    MIXED = "mixed"


class RelationKind(str, Enum):
    DEFINITION_APPLIES = "definition_applies"
    EXCEPTION_TO = "exception_to"
    CONDITION_FOR = "condition_for"
    PROCEDURE_FOR = "procedure_for"
    CROSS_REFERENCE = "cross_reference"
    OTHER_DEPENDENCY = "other_dependency"


def _not_blank(value: str, field_name: str) -> str:
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty")
    return value


class FileInput(StrictModel):
    source_id: str
    source_file: str
    file_type: Literal["pdf", "docx", "markdown", "text"]
    file_ref: str


class ExtractedTextBundle(StrictModel):
    source_id: str
    source_file: str
    text: str
    extraction_method: ExtractionMethod
    warnings: list[str] = Field(default_factory=list)

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        return _not_blank(value, "text")


class NormalizedTextInput(StrictModel):
    source_id: str
    source_file: str
    content_type: Literal["normalized_text", "markdown"]
    text: str
    source_type: DocumentSourceType = DocumentSourceType.UNKNOWN
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, value: str) -> str:
        return _not_blank(value, "text")


class DocumentCategory(StrictModel):
    category_scheme: Literal[
        "external_regulation_type",
        "internal_policy_type",
        "business_domain",
        "compliance_topic",
        "custom",
    ] = "custom"
    category_code: str | None = None
    category_label: str | None = None
    tags: list[str] = Field(default_factory=list)
    evidence_text: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    ambiguity_notes: list[str] = Field(default_factory=list)


class DocumentClassificationDraft(StrictModel):
    source_type: DocumentSourceType = DocumentSourceType.UNKNOWN
    issuer_type: IssuerType = IssuerType.UNKNOWN
    issuer_name: str | None = None
    categories: list[DocumentCategory] = Field(default_factory=list)
    topic_tags: list[str] = Field(default_factory=list)
    classification_tags: list[str] = Field(default_factory=list)
    evidence_text: list[str] = Field(default_factory=list)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    ambiguity_notes: list[str] = Field(default_factory=list)


class SourceLocation(StrictModel):
    kind: SourceLocationKind = SourceLocationKind.UNKNOWN
    value: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class TemporalMetadata(StrictModel):
    version_label: str | None = None
    effective_date_text: str | None = None
    promulgation_date_text: str | None = None
    repeal_date_text: str | None = None
    amendment_history_text: str | None = None
    validity_notes: list[str] = Field(default_factory=list)
    temporal_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    ambiguity_notes: list[str] = Field(default_factory=list)


class ExtractionProvenance(StrictModel):
    extraction_method: ExtractionMethod
    prompt_contract_version: str | None = None
    model_trace_id: str | None = None


class RegulationDocumentDraft(StrictModel):
    document_id: str
    source_id: str
    source_file: str
    classification: DocumentClassificationDraft
    title: str | None = None
    document_number: str | None = None
    document_status: DocumentStatus = DocumentStatus.UNKNOWN
    effective_date: date | None = None
    promulgation_date: date | None = None
    repeal_date: date | None = None
    temporal_metadata: TemporalMetadata
    parse_status: ParseStatus = ParseStatus.NEEDS_REVIEW
    warnings: list[str] = Field(default_factory=list)
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW


class HierarchyPath(StrictModel):
    part: str | None = None
    chapter: str | None = None
    section: str | None = None
    article_number: str | None = None
    article_title: str | None = None
    paragraph_number: str | None = None
    paragraph_index: int | None = None
    item_number: str | None = None
    item_label: str | None = None
    subitem_number: str | None = None
    heading_path: list[str] = Field(default_factory=list)


class SemanticUnitType(str, Enum):
    """Primary semantic category assigned to a regulation unit draft."""

    # Defines terms, concepts, or scoped meanings.
    DEFINITION = "definition"
    # Requires an actor to perform an action.
    OBLIGATION = "obligation"
    # Forbids an action or state.
    PROHIBITION = "prohibition"
    # Describes process, sequence, or procedural steps.
    PROCEDURE = "procedure"
    # Carves out an exception from another requirement.
    EXCEPTION = "exception"
    # States a condition, prerequisite, or dependency.
    CONDITION = "condition"
    # Requires reporting, filing, notice, or disclosure.
    REPORTING = "reporting"
    # Sets a numeric, date, amount, or threshold constraint.
    THRESHOLD = "threshold"
    # Grants permission, authority, or approval scope.
    AUTHORIZATION = "authorization"
    # Describes liability, consequence, or responsibility.
    LIABILITY = "liability"
    # Provides general context without a narrower semantic role.
    GENERAL = "general"
    # Semantic role was not determined.
    UNKNOWN = "unknown"


class SemanticUnitDraft(StrictModel):
    """Reviewable semantic extraction draft for one RegulationUnitDraft.

    This is not a RuleItem, an executable compliance rule, or a
    JudgmentResult. Extracted content should remain traceable to the unit's
    original_text or normalized_text. Medium/high-risk outputs should remain
    needs_review until approved by a human reviewer.
    """

    # Single primary semantic label for filtering, routing, and review UI.
    # If multiple legal effects exist, choose the dominant role and place
    # remaining facets in the detailed list fields.
    unit_type: SemanticUnitType = SemanticUnitType.UNKNOWN
    # Optional normalized title for the semantic draft.
    normalized_title: str | None = None
    # Brief human-reviewable summary of the unit.
    summary: str | None = None
    # Draft extracted definitions found in the unit.
    definitions: list[str] = Field(default_factory=list)
    # Draft obligations or duties found in the unit.
    obligations: list[str] = Field(default_factory=list)
    # Draft exceptions or carve-outs found in the unit.
    exceptions: list[str] = Field(default_factory=list)
    # Draft applicability statements for persons, entities, or contexts.
    applicability: list[str] = Field(default_factory=list)
    # Draft actors referenced by the unit.
    actors: list[str] = Field(default_factory=list)
    # Draft conditions or prerequisites referenced by the unit.
    conditions: list[str] = Field(default_factory=list)
    # Draft events that may trigger the unit.
    trigger_events: list[str] = Field(default_factory=list)
    # Draft actions required by the unit.
    required_actions: list[str] = Field(default_factory=list)
    # Draft actions prohibited by the unit.
    prohibited_actions: list[str] = Field(default_factory=list)
    # Draft timing, date, or deadline statements.
    deadlines: list[str] = Field(default_factory=list)
    # Draft numeric, amount, date, or limit thresholds.
    thresholds: list[str] = Field(default_factory=list)
    # Draft subject scope for covered actors or subjects.
    subject_scope: list[str] = Field(default_factory=list)
    # Draft object scope for covered objects or matters.
    object_scope: list[str] = Field(default_factory=list)
    # Draft reporting, filing, notice, or disclosure duties.
    reporting_obligations: list[str] = Field(default_factory=list)
    # Source excerpts supporting the draft semantic extraction.
    evidence_text: list[str] = Field(default_factory=list)
    # Draft confidence score for the semantic extraction.
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    # Review gate for draft semantic content.
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    # Notes on uncertainty, ambiguity, or competing interpretations.
    ambiguity_notes: list[str] = Field(default_factory=list)


class RegulationUnitDraft(StrictModel):
    unit_id: str
    document_id: str
    parent_unit_id: str | None = None
    order_index: int
    unit_level: int | None = None
    unit_kind: Literal[
        "part",
        "chapter",
        "section",
        "article",
        "paragraph",
        "item",
        "subitem",
        "appendix",
        "unknown",
    ] = "unknown"
    display_label: str | None = None
    source_id: str
    source_file: str
    source_location: SourceLocation
    hierarchy: HierarchyPath
    original_text: str
    normalized_text: str | None = None
    semantic_draft: SemanticUnitDraft
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    warnings: list[str] = Field(default_factory=list)

    @field_validator("original_text")
    @classmethod
    def original_text_must_not_be_empty(cls, value: str) -> str:
        return _not_blank(value, "original_text")

    @field_validator("order_index")
    @classmethod
    def order_index_must_be_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("order_index must be non-negative")
        return value


class ReferenceCandidate(StrictModel):
    candidate_id: str
    document_id: str
    from_unit_id: str
    target_label: str
    evidence_text: str
    source_location: SourceLocation | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    ambiguity_notes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DependencyEdgeDraft(StrictModel):
    edge_id: str
    document_id: str
    from_unit_id: str
    to_unit_id: str | None = None
    target_document_id: str | None = None
    target_document_title: str | None = None
    target_source_type: DocumentSourceType | None = None
    target_label: str | None = None
    target_scope: Literal["same_document", "external_document", "unknown"]
    resolution_status: Literal["resolved", "unresolved", "ambiguous"]
    relation_kind: RelationKind
    source_candidate_ids: list[str] = Field(default_factory=list)
    evidence_text: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    ambiguity_notes: list[str] = Field(default_factory=list)
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW

    @model_validator(mode="after")
    def validate_resolution_target(self) -> "DependencyEdgeDraft":
        has_target_label = bool(self.target_label and self.target_label.strip())
        has_target_document = any(
            value and value.strip()
            for value in (
                self.target_document_id,
                self.target_document_title,
                self.target_label,
            )
        )

        if (
            self.resolution_status == "resolved"
            and self.target_scope == "same_document"
            and not self.to_unit_id
        ):
            raise ValueError(
                "to_unit_id is required for resolved same-document dependencies"
            )

        if (
            self.resolution_status == "resolved"
            and self.target_scope == "external_document"
            and not has_target_document
        ):
            raise ValueError(
                "resolved external-document dependencies require a target identifier, "
                "title, or label"
            )

        if (
            self.resolution_status in {"unresolved", "ambiguous"}
            and not has_target_label
            and not self.ambiguity_notes
        ):
            raise ValueError(
                "unresolved or ambiguous dependencies require target_label or "
                "ambiguity_notes"
            )

        return self


RegulationUnitRelationDraft = DependencyEdgeDraft


class ResolvedDependencyGraphDraft(StrictModel):
    graph_id: str
    document_id: str
    reference_candidate_ids: list[str] = Field(default_factory=list)
    dependency_edges: list[DependencyEdgeDraft] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StructuringValidationFinding(StrictModel):
    stage: Literal[
        "input",
        "document",
        "unit",
        "semantic",
        "reference",
        "dependency",
        "output",
    ] = "output"
    target_type: Literal[
        "document",
        "unit",
        "semantic_draft",
        "reference_candidate",
        "dependency_edge",
        "pipeline_output",
        "unknown",
    ] = "unknown"
    target_id: str | None = None
    code: str
    severity: ValidationSeverity
    message: str
    document_id: str | None = None
    unit_id: str | None = None
    source_location: SourceLocation | None = None


class StructuringValidationReport(StrictModel):
    document_id: str
    summary: str
    findings: list[StructuringValidationFinding] = Field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    info_count: int = 0
    has_errors: bool = False

    @model_validator(mode="after")
    def sync_counts_and_has_errors(self) -> "StructuringValidationReport":
        self.error_count = sum(
            finding.severity is ValidationSeverity.ERROR for finding in self.findings
        )
        self.warning_count = sum(
            finding.severity is ValidationSeverity.WARNING for finding in self.findings
        )
        self.info_count = sum(
            finding.severity is ValidationSeverity.INFO for finding in self.findings
        )
        self.has_errors = self.error_count > 0
        return self


class StructuringPipelineOutput(StrictModel):
    contract_version: str = "v1"
    extraction_provenance: ExtractionProvenance
    document: RegulationDocumentDraft
    units: list[RegulationUnitDraft] = Field(default_factory=list)
    reference_candidates: list[ReferenceCandidate] = Field(default_factory=list)
    dependency_graph: ResolvedDependencyGraphDraft
    validation_report: StructuringValidationReport

    @field_validator("contract_version")
    @classmethod
    def contract_version_must_not_be_blank(cls, value: str) -> str:
        return _not_blank(value, "contract_version")

    @model_validator(mode="after")
    def validate_document_linkage(self) -> "StructuringPipelineOutput":
        document_id = self.document.document_id

        if self.validation_report.document_id != document_id:
            raise ValueError(
                "validation_report.document_id must match document.document_id"
            )

        if self.dependency_graph.document_id != document_id:
            raise ValueError(
                "dependency_graph.document_id must match document.document_id"
            )

        for unit in self.units:
            if unit.document_id != document_id:
                raise ValueError("unit.document_id must match document.document_id")

        for candidate in self.reference_candidates:
            if candidate.document_id != document_id:
                raise ValueError(
                    "reference_candidate.document_id must match document.document_id"
                )

        return self


SECRET_PATTERN = re.compile(
    r"(sk-[A-Za-z0-9_-]+|api[_-]?key|password|bearer\s+[A-Za-z0-9._-]+)",
    re.IGNORECASE,
)


__all__ = [
    "DependencyEdgeDraft",
    "DocumentCategory",
    "DocumentClassificationDraft",
    "DocumentSourceType",
    "DocumentStatus",
    "ExtractionMethod",
    "ExtractionProvenance",
    "ExtractedTextBundle",
    "FileInput",
    "HierarchyPath",
    "IssuerType",
    "NormalizedTextInput",
    "ParseStatus",
    "ReferenceCandidate",
    "RegulationDocumentDraft",
    "RegulationUnitDraft",
    "RegulationUnitRelationDraft",
    "RelationKind",
    "ResolvedDependencyGraphDraft",
    "ReviewStatus",
    "SECRET_PATTERN",
    "SemanticUnitDraft",
    "SemanticUnitType",
    "SourceLocation",
    "SourceLocationKind",
    "StructuringPipelineOutput",
    "StructuringValidationFinding",
    "StructuringValidationReport",
    "TemporalMetadata",
    "ValidationSeverity",
]
