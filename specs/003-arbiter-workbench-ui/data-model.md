# Data Model: Arbiter Workbench UI

## Enums

### ReviewDecision

- `approved`
- `rejected`
- `needs_changes`
- `needs_more_evidence`
- `superseded`

### ReviewTargetType

- `document`
- `unit`
- `semantic_draft`
- `reference_candidate`
- `dependency_edge`
- `curation_note`

### CurationNoteType

- `expert_note`
- `candidate_rule_hint`
- `scenario_example`
- `ambiguity_case`
- `dependency_issue`

### RuntimeDraftStatus

- `draft`
- `needs_review`
- `reviewed`

Runtime-facing outputs in this feature default to `draft` or `needs_review`.
They are display contracts only and are not final compliance decisions.

## Entities

### StructuringPipelineOutput

Existing 001 output consumed by the workbench.

Key expectations:
- Contains document metadata, units, semantic draft fields, evidence,
  validation findings, provenance, and review status.
- May be loaded from fixtures or exported JSON.
- Must be validated before the workbench opens it as editable review content.
- Frontend validation is a UI mirror only; the canonical 001 contract remains
  the existing Python/Pydantic schema.
- Must not be mutated in place by 003.

### DocumentMetadataReviewView

Reviewable display surface for document-level draft metadata from the loaded
001 output.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `title` | string or null | no | Draft title from the loaded output |
| `document_number` | string or null | no | Draft document number when present |
| `classification` | object or null | no | Draft document classification |
| `dates` | object | yes | Effective, promulgation, repeal, or related dates when present |
| `temporal_metadata` | object | yes | Version, amendment, and validity context |
| `warnings` | list[string] | yes | Document-level warnings |
| `validation_findings` | list[object] | yes | Source validation findings |
| `review_status` | string | yes | Review state from source or review artifact |

Validation rules:
- Missing metadata is shown as incomplete rather than inferred.
- Reviewing metadata must not mutate the loaded source JSON.

### SourceOutputRef

Stable reference used by all review and curation artifacts.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `contract_version` | string | yes | 001 output contract version or compatible fixture version |
| `document_id` | string | yes | Stable document identifier from the loaded output |
| `source_id` | string | yes | Stable source identifier from the loaded output |
| `source_file` | string | yes | Source label, not an absolute-path requirement |
| `loaded_at` | string | yes | Timestamp for when the workbench loaded the source output |

Validation rules:
- Hashes are not required.
- Missing identifiers make exported review/curation artifacts invalid.

### StructuringReviewPatch

Field-level reviewed edit artifact.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_output_ref` | SourceOutputRef | yes | Links back to the loaded 001 output |
| `target_type` | ReviewTargetType | yes | Generic reviewed target type |
| `target_id` | string | yes | ID for the reviewed document, unit, draft, candidate, edge, or note |
| `unit_id` | string or null | no | Present for unit-level edits when applicable |
| `field_path` | string | yes | Review-visible path to the edited field |
| `old_value` | JSON value | yes | Value observed in the loaded source output |
| `new_value` | JSON value | yes | Reviewer-proposed replacement |
| `reviewer_note` | string | no | Human explanation or evidence note |
| `reviewer_decision` | ReviewDecision | yes | Review decision for this field edit |
| `reviewed_at` | string | yes | Review timestamp |
| `reviewer_identity` | string or null | no | Reviewer identity when available |

Validation rules:
- `old_value` must reflect the loaded source value at the time of edit.
- Patch export must not duplicate full original regulation text unless the
  edited field itself is that text.
- Multiple unsaved edits to the same target and `field_path` must make clear
  whether export produces a patch sequence or the latest consolidated patch.
- Patches do not promote assets into runtime-safe reviewed assets.
- Identity management is outside this feature.

### StructuringReviewDecision

Target-level review decision artifact.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_output_ref` | SourceOutputRef | yes | Links back to the loaded 001 output |
| `target_type` | ReviewTargetType | yes | Document, unit, semantic draft, reference candidate, dependency edge, or curation note |
| `target_id` | string | yes | Stable target identifier |
| `unit_id` | string or null | no | Present when the decision is associated with a regulation unit |
| `reviewer_decision` | ReviewDecision | yes | Decision outcome |
| `reviewer_note` | string | no | Human-readable rationale |
| `reviewed_at` | string | yes | Decision timestamp |
| `reviewer_identity` | string or null | no | Reviewer identity when available |

Validation rules:
- Decisions remain review artifacts only.
- A decision may reference an `AssetCurationRecord`, but it must not generate a
  formal `RuleItem`, active `RulePack`, or final judgment.
- Identity management is outside this feature.

### AssetCurationRecord

Optional expert curation note used to accumulate data-asset review knowledge.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_output_ref` | SourceOutputRef | yes | Links back to the loaded 001 output |
| `curation_id` | string | yes | Stable workbench-generated note ID |
| `note_type` | CurationNoteType | yes | Expert note, candidate rule hint, scenario example, ambiguity case, or dependency issue |
| `target_type` | ReviewTargetType | no | Optional related review target |
| `target_id` | string | no | Optional related target ID |
| `unit_id` | string or null | no | Optional related unit ID |
| `note` | string | yes | Expert-authored note |
| `created_at` | string | yes | Creation timestamp |
| `review_status` | string | yes | Defaults to `needs_review` |
| `reviewer_identity` | string or null | no | Reviewer identity when available |

Validation rules:
- Curation records are not active rules, formal rule items, reviewed runtime
  assets, final judgments, or final compliance conclusions.
- Candidate rule hints are clues for later expert work only.
- Identity management is outside this feature.

### RuntimeScenarioInput

Placeholder frontend-facing scenario input contract.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `scenario_id` | string | yes | Workbench-generated ID |
| `question` | string | yes | Natural-language compliance question |
| `structured_fields` | object | no | Optional business scenario fields |
| `as_of_date` | string or null | no | Date basis when provided |

Validation rules:
- This is not a final 002 runtime input schema.
- Submission is allowed only through mocked or future 002 adapters.

### RuntimeJudgmentDraftView

Placeholder frontend-facing judgment draft display contract.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `draft_id` | string | yes | Stable draft display ID |
| `scenario_id` | string | yes | Links to `RuntimeScenarioInput` |
| `status` | RuntimeDraftStatus | yes | Usually `draft` or `needs_review` |
| `summary` | string | yes | Draft answer summary |
| `confidence` | number or null | no | Adapter-provided confidence |
| `warnings` | list[string] | yes | Display warnings |
| `validation_status` | string | yes | Adapter-provided validation status |
| `human_review_required` | boolean | yes | Review gate indicator |
| `citations` | list[RuntimeCitationView] | yes | Supporting citations |
| `evidence` | list[RuntimeEvidenceView] | yes | Supporting evidence |
| `trace` | RuntimeTraceView | no | Sanitized trace summary |

Validation rules:
- Must be labeled as non-final.
- Must not be treated as `JudgmentResult`.
- Must remain replaceable once 002 finalizes its runtime schemas.
- Must not be treated as a backend or domain-level 002 schema.

### RuntimeCitationView

Placeholder frontend-facing citation display contract.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `citation_id` | string | yes | Stable citation ID |
| `unit_id` | string | yes | Stable regulation unit ID |
| `document_id` | string | yes | Source document ID |
| `source_version` | string or null | no | Version label when available |
| `article_or_clause` | string or null | no | Article or clause number when available |
| `provenance` | string or null | no | Adapter-provided provenance |
| `as_of_date` | string or null | no | Interpretation date basis |

Validation rules:
- Missing `unit_id` or `document_id` makes the citation incomplete.
- Free-text citation labels alone are insufficient.
- Must remain replaceable once 002 finalizes its runtime schemas.

### RuntimeEvidenceView

Placeholder frontend-facing evidence display contract.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `evidence_id` | string | yes | Stable evidence ID |
| `unit_id` | string | no | Related regulation unit when available |
| `excerpt` | string | no | Bounded evidence excerpt |
| `dependency_context` | list[string] | yes | Related dependency context supplied by adapter |
| `provenance` | string or null | no | Adapter-provided provenance |
| `as_of_date` | string or null | no | Date basis when supplied |

Validation rules:
- Evidence display must not fabricate missing source fields.
- Large or sensitive raw content must be bounded or redacted.
- Must remain replaceable once 002 finalizes its runtime schemas.

### RuntimeTraceView

Placeholder frontend-facing sanitized trace display contract.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `trace_id` | string | yes | Stable trace ID |
| `steps` | list[object] | yes | Sanitized trace summaries |
| `redaction_warnings` | list[string] | yes | Redaction/blocking notes |

Validation rules:
- Must not expose secrets, full prompts, provider payloads, or unnecessary
  sensitive raw text.
- Trace display is inspection-only and does not execute runtime logic.
- Must remain replaceable once 002 finalizes its runtime schemas.

## State Rules

- Loaded 001 source JSON remains immutable in the workbench.
- Invalid or schema-incompatible `StructuringPipelineOutput` creates no
  editable review session.
- Unsaved edits are local draft UI state until exported.
- Exported patches, decisions, and curation records are separate artifacts.
- Runtime-facing outputs are placeholder drafts unless a future adapter marks a
  display-only status otherwise.
- No artifact in this feature becomes active `RulePack`, formal `RuleItem`,
  runtime-safe reviewed asset, final `JudgmentResult`, or final compliance
  conclusion.
