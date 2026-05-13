# Contract: Offline Regulation Structuring Pipeline

**Contract version**: `v1`
**Scope**: Offline/admin only
**Out of scope**: Frontend UI, ComplianceJudgmentAgent, JudgmentResult, active
RulePack, formal RuleItem, asset promotion, production review workflow, and
runtime agent answers

## Operation

`structure_regulation(input) -> StructuringPipelineOutput`

The operation accepts normalized text or Markdown content and returns a
schema-backed JSON-serializable draft output bundle. It uses a hybrid strategy:
deterministic code handles intake, source preservation, obvious structural
hints, stable source_id / document_id linkage, JSON serialization, schema
validation, and validation reports;
LLM-assisted extraction handles variable-format hierarchy interpretation,
semantic unit extraction, article/paragraph boundary proposals, document
classification, definitions, obligations, exceptions, actors, conditions,
applicability, reference candidates, and draft dependency edges.

## Optional Intake Adapter Boundary

PDF and Word are not direct first-slice request content types. Future upload or
file-extraction features may connect through:

`FileInput -> ExtractedTextBundle -> NormalizedTextInput`

This contract does not implement OCR, password handling, or full layout
recovery.

## Request Schema

```json
{
  "contract_version": "v1",
  "source_id": "string",
  "source_file": "string",
  "content_type": "normalized_text | markdown",
  "source_type": "external_regulation | internal_policy | unknown",
  "text": "string",
  "metadata": {
    "title": "string or null",
    "issuer_type": "government_regulator | self_regulatory_organization | internal_org | external_other | unknown",
    "issuer_name": "string or null",
    "category_tags": ["string"],
    "topic_tags": ["string"],
    "document_status": "official | draft_for_comment | deprecated | unknown",
    "effective_date": "YYYY-MM-DD or null",
    "promulgation_date": "YYYY-MM-DD or null",
    "repeal_date": "YYYY-MM-DD or null",
    "version_label": "string or null",
    "amendment_history_text": "string or null",
    "validity_notes": ["string"]
  }
}
```

Required behavior:
- `text` must be non-empty after trimming.
- `source_type` may be omitted by callers and defaults to `unknown` in the
  output classification.
- `source_file` is a traceability label and must not require an absolute local
  path.
- PDF and Word are not direct request content types for this first slice. They
  may be handled by the optional intake adapter only after extractable text
  exists.
- All model calls must go through LLMClient / ModelProvider.
- Model provider settings and secrets are not part of this request contract.

## Success Response Schema

```json
{
  "contract_version": "v1",
  "extraction_provenance": {
    "extraction_method": "deterministic | llm_assisted | mixed",
    "prompt_contract_version": "string or null",
    "model_trace_id": "string or null"
  },
  "document": {
    "document_id": "string",
    "source_id": "string",
    "source_file": "string",
    "classification": {
      "source_type": "external_regulation | internal_policy | unknown",
      "issuer_type": "government_regulator | self_regulatory_organization | internal_org | external_other | unknown",
      "issuer_name": "string or null",
      "categories": [
        {
          "category_code": "string or null",
          "category_label": "string or null",
          "tags": ["string"],
          "evidence_text": "string or null",
          "confidence": "number or null",
          "ambiguity_notes": ["string"]
        }
      ],
      "topic_tags": ["string"],
      "classification_tags": ["string"],
      "evidence_text": ["string"],
      "confidence": "number or null",
      "review_status": "needs_review",
      "ambiguity_notes": ["string"]
    },
    "title": "string or null",
    "document_status": "official | draft_for_comment | deprecated | unknown",
    "effective_date": "YYYY-MM-DD or null",
    "promulgation_date": "YYYY-MM-DD or null",
    "repeal_date": "YYYY-MM-DD or null",
    "temporal_metadata": {
      "version_label": "string or null",
      "amendment_history_text": "string or null",
      "validity_notes": ["string"],
      "temporal_confidence": "number or null",
      "ambiguity_notes": ["string"]
    },
    "parse_status": "needs_review",
    "warnings": ["string"]
  },
  "units": [
    {
      "unit_id": "string",
      "document_id": "string",
      "parent_unit_id": "string or null",
      "order_index": "integer",
      "display_label": "string or null",
      "source_id": "string",
      "source_file": "string",
      "source_location": {
        "kind": "page_number | line_number | paragraph_index | heading_path | unknown",
        "value": "string or null",
        "confidence": "string or null"
      },
      "hierarchy": {
        "chapter": "string or null",
        "section": "string or null",
        "article_number": "string or null",
        "article_title": "string or null",
        "paragraph_index": "integer or null",
        "item_label": "string or null"
      },
      "original_text": "string",
      "normalized_text": "string or null",
      "semantic_draft": {
        "unit_type": "string or null",
        "normalized_title": "string or null",
        "definitions": ["string"],
        "obligations": ["string"],
        "exceptions": ["string"],
        "applicability": ["string"],
        "actors": ["string"],
        "conditions": ["string"],
        "trigger_events": ["string"],
        "required_actions": ["string"],
        "prohibited_actions": ["string"],
        "deadlines": ["string"],
        "thresholds": ["string"],
        "subject_scope": ["string"],
        "object_scope": ["string"],
        "reporting_obligations": ["string"],
        "evidence_text": ["string"],
        "confidence": "number or null",
        "review_status": "needs_review",
        "ambiguity_notes": ["string"]
      },
      "review_status": "needs_review",
      "warnings": ["string"]
    }
  ],
  "reference_candidates": [
    {
      "candidate_id": "string",
      "document_id": "string",
      "from_unit_id": "string",
      "target_label": "string",
      "evidence_text": "string",
      "source_location": {
        "kind": "page_number | line_number | paragraph_index | heading_path | unknown",
        "value": "string or null",
        "confidence": "string or null"
      },
      "confidence": "number or null",
      "ambiguity_notes": ["string"],
      "warnings": ["string"]
    }
  ],
  "dependency_graph": {
    "graph_id": "string",
    "document_id": "string",
    "reference_candidate_ids": ["string"],
    "dependency_edges": [
      {
        "edge_id": "string",
        "document_id": "string",
        "from_unit_id": "string",
        "to_unit_id": "string or null",
        "target_document_id": "string or null",
        "target_document_title": "string or null",
        "target_source_type": "external_regulation | internal_policy | unknown | null",
        "target_label": "string or null",
        "target_scope": "same_document | external_document | unknown",
        "resolution_status": "resolved | unresolved | ambiguous",
        "relation_kind": "definition_applies | exception_to | condition_for | procedure_for | cross_reference | other_dependency",
        "source_candidate_ids": ["string"],
        "evidence_text": "string",
        "confidence": "number or null",
        "ambiguity_notes": ["string"],
        "review_status": "needs_review"
      }
    ],
    "warnings": ["string"]
  },
  "validation_report": {
    "document_id": "string",
    "summary": "string",
    "findings": [
      {
        "code": "string",
        "severity": "info | warning | error",
        "message": "string",
        "document_id": "string or null",
        "unit_id": "string or null",
        "source_location": {
          "kind": "page_number | line_number | paragraph_index | heading_path | unknown",
          "value": "string or null",
          "confidence": "string or null"
        }
      }
    ],
    "has_errors": true
  }
}
```

Required behavior:
- Document drafts default to `parse_status = needs_review`.
- Document classification drafts default to `review_status = needs_review`.
- Semantic unit drafts, unit drafts, and dependency edge drafts default to
  `review_status = needs_review`.
- `ReviewStatus` also reserves `approved`, `rejected`, and `superseded` for
  later review or promotion workflows. This pipeline must not assign those
  statuses.
- `HierarchyPath` preserves source document labels. `parent_unit_id` and
  `order_index` support explicit tree navigation and stable review UI rendering.
- Temporal metadata preserves version, amendment, validity, confidence, and
  ambiguity context when available. Missing or uncertain temporal facts stay
  null or explicit review notes.
- Extraction provenance must not contain secrets, full prompts, provider
  payloads, or unnecessary raw sensitive text.
- All LLM outputs must be constrained by the Pydantic schemas represented by
  this contract before entering downstream output.
- LLM output schema validation failures must be reported in
  `StructuringValidationReport` or structured errors and must not silently enter
  the success output.
- Temporal ambiguity, invalid tree links, missing provenance, and unsupported
  review-status assignment must be reported as validation findings or structured
  errors.
- LLM outputs must include `evidence_text`, `ambiguity_notes`, `confidence`, or
  validation findings where applicable.
- `DocumentSourceType` distinguishes external regulations from internal
  policies, while detailed compliance topics remain extensible through
  `DocumentCategory`, `topic_tags`, and `classification_tags`.
- `DocumentCategory` is not an exhaustive business taxonomy.
- Metadata classification hints remain draft inputs and do not create reviewed
  classification state.
- ReferenceCandidate records are textual clues; DependencyEdgeDraft /
  RegulationUnitRelationDraft records are proposed resolved edges.
- In this contract, RegulationUnitRelationDraft is a compatibility alias for the
  same draft edge schema as DependencyEdgeDraft.
- DependencyEdgeDraft records may represent resolved, unresolved, or ambiguous
  references. `to_unit_id` may be null when the target is unresolved, ambiguous,
  external, or unknown.
- `target_document_id` may be populated when a proposed edge points to a known
  external document; unresolved external references preserve `target_label` and
  may leave `target_document_id` null.
- Cross-document links between internal policies and external regulations
  preserve `target_document_id`, `target_document_title`, and
  `target_source_type` when available.
- The graph references top-level ReferenceCandidate records by ID instead of
  duplicating full objects.
- Proposed edges remain draft unless approved by a later human review workflow.
  All relation kinds remain draft interpretations, and no dependency edge is a
  final legal interpretation.
- SemanticUnitDraft fields may be initialized with empty lists, null scalar
  values, and ambiguity notes when extraction cannot produce a validated result.
- Success output must not contain JudgmentResult, active RulePack, formal
  RuleItem, final legal judgment, or runtime agent answers.
- StructuringPipelineOutput is not runtime-safe. A later review/promotion
  workflow must convert approved drafts into reviewed runtime assets before Agent
  Runtime can consume them.

## Structured Error Response

```json
{
  "contract_version": "v1",
  "error": {
    "code": "string",
    "message": "string",
    "source_id": "string or null",
    "source_file": "string or null",
    "details": [
      {
        "code": "string",
        "message": "string"
      }
    ]
  }
}
```

Errors are used for non-reviewable inputs, such as empty text, unsupported
direct content type, or unsupported/invalid model output that prevents a
reviewable draft. Reviewable ambiguity is represented in
`StructuringValidationReport` instead.
