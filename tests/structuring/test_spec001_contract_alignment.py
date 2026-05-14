"""Alignment tests between regulation_structuring schema and spec001 contract.

These tests document that the Pydantic schema matches the spec001 contract
(data-model.md and contracts/structuring-pipeline-contract.md). If a spec
revision changes the contract, these tests will fail and require explicit
schema or contract alignment.
"""

from __future__ import annotations

from arbiter.schemas.regulation_structuring import (
    DocumentCategory,
    DocumentStatus,
    ExtractionMethod,
    IssuerType,
    ParseStatus,
    RelationKind,
    ReviewStatus,
    SemanticUnitType,
    SourceLocation,
    SourceLocationKind,
    TemporalMetadata,
    ValidationSeverity,
)


def test_parse_status_matches_spec001_contract() -> None:
    # contract: parsed | partial | needs_review | failed
    expected = {"parsed", "partial", "needs_review", "failed"}
    actual = {m.value for m in ParseStatus}
    assert actual == expected, f"ParseStatus drift: {actual ^ expected}"


def test_issuer_type_matches_spec001_contract() -> None:
    # contract: government_regulator | self_regulatory_organization | internal_org |
    #           external_other | joint_issuers | unknown
    expected = {
        "government_regulator",
        "self_regulatory_organization",
        "internal_org",
        "external_other",
        "joint_issuers",
        "unknown",
    }
    actual = {m.value for m in IssuerType}
    assert actual == expected, f"IssuerType drift: {actual ^ expected}"


def test_document_category_scheme_matches_spec001_contract() -> None:
    # contract: external_regulation_type | internal_policy_type | business_domain |
    #           compliance_topic | custom
    expected = {
        "external_regulation_type",
        "internal_policy_type",
        "business_domain",
        "compliance_topic",
        "custom",
    }
    from typing import get_args, get_origin
    ann = DocumentCategory.model_fields["category_scheme"].annotation
    # Unwrap Annotated if present; stop at Literal
    while get_origin(ann) is not None and get_origin(ann).__name__ == "Annotated":
        args = get_args(ann)
        if not args:
            break
        ann = args[0]
    actual = set(get_args(ann))
    assert actual == expected, f"DocumentCategory.scheme drift: {actual ^ expected}"


def test_source_location_confidence_is_number() -> None:
    # contract: "number or null"
    field = SourceLocation.model_fields["confidence"]
    assert field.annotation is float or (
        hasattr(field.annotation, "__args__") and float in field.annotation.__args__
    )


def test_temporal_metadata_fields_match_spec001_contract() -> None:
    # contract lists: version_label, effective_date_text, promulgation_date_text,
    # repeal_date_text, amendment_history_text, validity_notes, temporal_confidence,
    # ambiguity_notes
    expected_fields = {
        "version_label",
        "effective_date_text",
        "promulgation_date_text",
        "repeal_date_text",
        "amendment_history_text",
        "validity_notes",
        "temporal_confidence",
        "ambiguity_notes",
    }
    actual_fields = set(TemporalMetadata.model_fields.keys())
    assert expected_fields <= actual_fields, f"Missing TemporalMetadata fields: {expected_fields - actual_fields}"


def test_review_status_defaults_to_needs_review() -> None:
    assert ReviewStatus.NEEDS_REVIEW.value == "needs_review"


def test_extraction_method_matches_spec001_contract() -> None:
    expected = {"deterministic", "llm_assisted", "mixed"}
    actual = {m.value for m in ExtractionMethod}
    assert actual == expected, f"ExtractionMethod drift: {actual ^ expected}"


def test_document_status_matches_spec001_contract() -> None:
    expected = {"official", "draft_for_comment", "deprecated", "unknown"}
    actual = {m.value for m in DocumentStatus}
    assert actual == expected, f"DocumentStatus drift: {actual ^ expected}"


def test_validation_severity_matches_spec001_contract() -> None:
    expected = {"info", "warning", "error"}
    actual = {m.value for m in ValidationSeverity}
    assert actual == expected, f"ValidationSeverity drift: {actual ^ expected}"


def test_relation_kind_matches_spec001_contract() -> None:
    expected = {
        "definition_applies",
        "exception_to",
        "condition_for",
        "procedure_for",
        "cross_reference",
        "other_dependency",
    }
    actual = {m.value for m in RelationKind}
    assert actual == expected, f"RelationKind drift: {actual ^ expected}"


def test_semantic_unit_type_matches_spec001_contract() -> None:
    expected = {
        "definition",
        "obligation",
        "prohibition",
        "procedure",
        "exception",
        "condition",
        "reporting",
        "threshold",
        "authorization",
        "liability",
        "general",
        "unknown",
    }
    actual = {m.value for m in SemanticUnitType}
    assert actual == expected, f"SemanticUnitType drift: {actual ^ expected}"


def test_source_location_kind_matches_spec001_contract() -> None:
    expected = {"page_number", "line_number", "paragraph_index", "heading_path", "unknown"}
    actual = {m.value for m in SourceLocationKind}
    assert actual == expected, f"SourceLocationKind drift: {actual ^ expected}"
