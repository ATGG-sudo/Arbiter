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
    category_code: str | None = None
    category_label: str | None = None
    tags: list[str] = Field(default_factory=list)
    evidence_text: str | None = None
    confidence: float | None = None
    ambiguity_notes: list[str] = Field(default_factory=list)


class DocumentClassificationDraft(StrictModel):
    source_type: DocumentSourceType = DocumentSourceType.UNKNOWN
    issuer_type: IssuerType = IssuerType.UNKNOWN
    issuer_name: str | None = None
    categories: list[DocumentCategory] = Field(default_factory=list)
    topic_tags: list[str] = Field(default_factory=list)
    classification_tags: list[str] = Field(default_factory=list)
    evidence_text: list[str] = Field(default_factory=list)
    confidence: float | None = None
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    ambiguity_notes: list[str] = Field(default_factory=list)


class SourceLocation(StrictModel):
    kind: SourceLocationKind = SourceLocationKind.UNKNOWN
    value: str | None = None
    confidence: str | None = None


class TemporalMetadata(StrictModel):
    version_label: str | None = None
    amendment_history_text: str | None = None
    validity_notes: list[str] = Field(default_factory=list)
    temporal_confidence: float | None = None
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
    document_status: DocumentStatus = DocumentStatus.UNKNOWN
    effective_date: date | None = None
    promulgation_date: date | None = None
    repeal_date: date | None = None
    temporal_metadata: TemporalMetadata
    parse_status: ParseStatus = ParseStatus.NEEDS_REVIEW
    warnings: list[str] = Field(default_factory=list)


class HierarchyPath(StrictModel):
    chapter: str | None = None
    section: str | None = None
    article_number: str | None = None
    article_title: str | None = None
    paragraph_index: int | None = None
    item_label: str | None = None


class SemanticUnitDraft(StrictModel):
    unit_type: str | None = None
    normalized_title: str | None = None
    definitions: list[str] = Field(default_factory=list)
    obligations: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    applicability: list[str] = Field(default_factory=list)
    actors: list[str] = Field(default_factory=list)
    conditions: list[str] = Field(default_factory=list)
    trigger_events: list[str] = Field(default_factory=list)
    required_actions: list[str] = Field(default_factory=list)
    prohibited_actions: list[str] = Field(default_factory=list)
    deadlines: list[str] = Field(default_factory=list)
    thresholds: list[str] = Field(default_factory=list)
    subject_scope: list[str] = Field(default_factory=list)
    object_scope: list[str] = Field(default_factory=list)
    reporting_obligations: list[str] = Field(default_factory=list)
    evidence_text: list[str] = Field(default_factory=list)
    confidence: float | None = None
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW
    ambiguity_notes: list[str] = Field(default_factory=list)


class RegulationUnitDraft(StrictModel):
    unit_id: str
    document_id: str
    parent_unit_id: str | None = None
    order_index: int
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
    confidence: float | None = None
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
    confidence: float | None = None
    ambiguity_notes: list[str] = Field(default_factory=list)
    review_status: ReviewStatus = ReviewStatus.NEEDS_REVIEW


RegulationUnitRelationDraft = DependencyEdgeDraft


class ResolvedDependencyGraphDraft(StrictModel):
    graph_id: str
    document_id: str
    reference_candidate_ids: list[str] = Field(default_factory=list)
    dependency_edges: list[DependencyEdgeDraft] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class StructuringValidationFinding(StrictModel):
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
    has_errors: bool = False

    @model_validator(mode="after")
    def sync_has_errors(self) -> "StructuringValidationReport":
        self.has_errors = any(
            finding.severity is ValidationSeverity.ERROR for finding in self.findings
        )
        return self


class StructuringPipelineOutput(StrictModel):
    contract_version: str = "v1"
    extraction_provenance: ExtractionProvenance
    document: RegulationDocumentDraft
    units: list[RegulationUnitDraft] = Field(default_factory=list)
    reference_candidates: list[ReferenceCandidate] = Field(default_factory=list)
    dependency_graph: ResolvedDependencyGraphDraft
    validation_report: StructuringValidationReport


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
    "SourceLocation",
    "SourceLocationKind",
    "StructuringPipelineOutput",
    "StructuringValidationFinding",
    "StructuringValidationReport",
    "TemporalMetadata",
    "ValidationSeverity",
]
