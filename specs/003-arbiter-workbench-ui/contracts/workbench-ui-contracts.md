# Contract: Arbiter Workbench UI

**Contract status**: Frontend-facing planning contract  
**Scope**: Expert curation of 001 outputs and placeholder runtime-facing UI  
**Out of scope**: 001 pipeline execution, 002 Agent Runtime, retrieval, vector
search, rule execution, LLM calls, active `RulePack`, formal `RuleItem`, final
`JudgmentResult`, final compliance conclusions, PDF/DOCX parsing, backend
services, database storage, authentication, and API routes.

## Input: Structuring Output Load

The workbench accepts fixture or exported JSON conforming to 001
`StructuringPipelineOutput`.

Required behavior:
- Validate the loaded shape before displaying it as editable review content.
- Treat frontend validation as a UI mirror only; the canonical 001 contract
  remains the existing Python/Pydantic schema.
- Reject invalid or schema-incompatible input with readable validation feedback
  and no editable review session.
- Preserve the loaded JSON as read-only source data.
- Display missing source, hierarchy, evidence, temporal, or review-status fields
  as incomplete instead of fabricating values.
- Allow MVP validation without running the 001 pipeline.

## DocumentMetadataReviewView

```json
{
  "title": "Sample Policy",
  "document_number": "POL-001",
  "classification": {
    "source_type": "internal_policy",
    "review_status": "needs_review"
  },
  "dates": {
    "effective_date": "2026-05-13",
    "promulgation_date": null,
    "repeal_date": null
  },
  "temporal_metadata": {
    "version_label": "v1",
    "validity_notes": []
  },
  "warnings": [],
  "validation_findings": [],
  "review_status": "needs_review"
}
```

Required behavior:
- Display fields as reviewable metadata.
- Do not mutate the loaded source JSON.
- Show missing fields as incomplete.

## SourceOutputRef

```json
{
  "contract_version": "v1",
  "document_id": "doc-001",
  "source_id": "source-001",
  "source_file": "sample-policy.md",
  "loaded_at": "2026-05-13T00:00:00Z"
}
```

Hashes are not required.

## StructuringReviewPatch

```json
{
  "source_output_ref": {
    "contract_version": "v1",
    "document_id": "doc-001",
    "source_id": "source-001",
    "source_file": "sample-policy.md",
    "loaded_at": "2026-05-13T00:00:00Z"
  },
  "target_type": "semantic_draft",
  "target_id": "unit-001.semantic_draft",
  "unit_id": "unit-001",
  "field_path": "units[0].semantic_draft.obligations[0]",
  "old_value": "draft obligation text",
  "new_value": "reviewed obligation text",
  "reviewer_note": "Clarified wording against source evidence.",
  "reviewer_decision": "needs_changes",
  "reviewed_at": "2026-05-13T00:10:00Z",
  "reviewer_identity": "reviewer-id-if-available"
}
```

Required behavior:
- Export reviewed edits without mutating source JSON in place.
- Keep `old_value` tied to the loaded source value.
- Make clear whether repeated unsaved edits to the same target and `field_path`
  export as a patch sequence or the latest consolidated patch.
- Do not promote edited values into active rules or runtime-safe assets.
- Treat `reviewer_identity` as optional; identity management is outside this
  feature.

## StructuringReviewDecision

```json
{
  "source_output_ref": {
    "contract_version": "v1",
    "document_id": "doc-001",
    "source_id": "source-001",
    "source_file": "sample-policy.md",
    "loaded_at": "2026-05-13T00:00:00Z"
  },
  "target_type": "dependency_edge",
  "target_id": "edge-001",
  "unit_id": "unit-001",
  "reviewer_decision": "needs_more_evidence",
  "reviewer_note": "Target unit is ambiguous.",
  "reviewed_at": "2026-05-13T00:12:00Z",
  "reviewer_identity": "reviewer-id-if-available"
}
```

Allowed `target_type` values:
- `document`
- `unit`
- `semantic_draft`
- `reference_candidate`
- `dependency_edge`
- `curation_note`

## AssetCurationRecord

```json
{
  "source_output_ref": {
    "contract_version": "v1",
    "document_id": "doc-001",
    "source_id": "source-001",
    "source_file": "sample-policy.md",
    "loaded_at": "2026-05-13T00:00:00Z"
  },
  "curation_id": "curation-001",
  "note_type": "scenario_example",
  "target_type": "unit",
  "target_id": "unit-001",
  "unit_id": "unit-001",
  "note": "Useful future scenario: investment approval threshold review.",
  "created_at": "2026-05-13T00:15:00Z",
  "review_status": "needs_review",
  "reviewer_identity": "reviewer-id-if-available"
}
```

Allowed `note_type` values:
- `expert_note`
- `candidate_rule_hint`
- `scenario_example`
- `ambiguity_case`
- `dependency_issue`

These records are curation material only.

## RuntimeScenarioInput

```json
{
  "scenario_id": "scenario-001",
  "question": "Can this investment proceed under the current policy?",
  "structured_fields": {
    "transaction_type": "investment",
    "amount": "example only"
  },
  "as_of_date": "2026-05-13"
}
```

This is a placeholder UI contract, not a final 002 input schema.

## RuntimeJudgmentDraftView

```json
{
  "draft_id": "draft-001",
  "scenario_id": "scenario-001",
  "status": "draft",
  "summary": "Mock judgment draft for UI inspection only.",
  "confidence": 0.72,
  "warnings": ["Mock response"],
  "validation_status": "needs_review",
  "human_review_required": true,
  "citations": [],
  "evidence": [],
  "trace": {
    "trace_id": "trace-001",
    "steps": [],
    "redaction_warnings": []
  }
}
```

Required behavior:
- Label as draft and non-final.
- Render only data supplied by a mocked or future adapter.
- Do not call LLMs, retrieval, rule execution, or 002 runtime logic.
- Remain replaceable once 002 finalizes its runtime schemas.
- Must not be treated as backend or domain-level 002 schemas.

## RuntimeCitationView

```json
{
  "citation_id": "citation-001",
  "unit_id": "unit-001",
  "document_id": "doc-001",
  "source_version": "v1",
  "article_or_clause": "Article 1",
  "provenance": "mock-adapter",
  "as_of_date": "2026-05-13"
}
```

Required behavior:
- Flag missing `unit_id` or `document_id` as incomplete.
- Treat free-text-only labels as insufficient.

## RuntimeEvidenceView

```json
{
  "evidence_id": "evidence-001",
  "unit_id": "unit-001",
  "excerpt": "Bounded evidence excerpt.",
  "dependency_context": ["edge-001"],
  "provenance": "mock-adapter",
  "as_of_date": "2026-05-13"
}
```

## RuntimeTraceView

```json
{
  "trace_id": "trace-001",
  "steps": [
    {
      "step_id": "step-001",
      "label": "Mock adapter returned draft",
      "status": "completed"
    }
  ],
  "redaction_warnings": []
}
```

Required behavior:
- Show sanitized summaries only.
- Block or redact secrets, full prompts, provider payloads, and unnecessary
  sensitive raw text.
