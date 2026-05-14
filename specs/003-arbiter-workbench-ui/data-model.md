# Data Model: Arbiter Workbench UI

## Enums

### WorkbenchInputKind

- `markdown`
- `structuring_output_json`

### StructuringRunStatus

- `idle`
- `running`
- `succeeded`
- `failed`
- `validation_failed`
- `cancelled`

### ReviewDecision

- `approved`
- `rejected`
- `needs_changes`
- `needs_more_evidence`
- `not_applicable`
- `superseded`

### ReviewTargetType

- `document`
- `unit`
- `semantic_draft`
- `reference_candidate`
- `dependency_edge`
- `curation_note`

### IntegratedPackageStatus

- `needs_review`
- `reviewed_for_structuring`

`reviewed_for_structuring` is an Admin review status only. It does not make the
package runtime-safe and does not promote rules.

## Entities

### MarkdownRegulationInput

Markdown regulation or internal-policy source entered in the UI.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `input_kind` | WorkbenchInputKind | yes | `markdown` |
| `source_id` | string | yes | Workbench-generated or user-provided source ID |
| `source_file` | string | yes | Upload file name or UI label |
| `raw_markdown` | string | yes | Source Markdown snapshot |
| `source_type` | string | no | external regulation, internal policy, or unknown |
| `metadata` | object | yes | Optional title, document number, date, issuer, topic hints |

Validation rules:
- `raw_markdown` must not be empty after trimming.
- PDF and Word are not accepted here.
- This input is converted to 001 `NormalizedTextInput` by the Admin adapter.

### StructuringRunRequest

UI-to-Admin-adapter request for LLM-assisted 001 structuring.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `request_id` | string | yes | Workbench-generated request ID |
| `input` | MarkdownRegulationInput | yes | Source Markdown and metadata |
| `llm_assisted` | boolean | yes | Whether the adapter should use configured ModelProvider |
| `model_mode` | string | yes | `configured_provider` or `mock_provider` for tests |
| `requested_at` | string | yes | Timestamp |

Validation rules:
- Frontend must not include provider secrets.
- `llm_assisted=true` means the Admin adapter may use the configured
  `ModelProvider`; it does not authorize frontend model calls.

### StructuringRunResult

Adapter response after invoking 001 structuring.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `request_id` | string | yes | Links to request |
| `run_id` | string | yes | Adapter-generated run ID |
| `status` | StructuringRunStatus | yes | Result state |
| `output` | StructuringPipelineOutput or null | no | Present only when valid output exists |
| `errors` | list[object] | yes | Structured errors |
| `warnings` | list[string] | yes | Non-blocking warnings |
| `sanitized_trace` | object or null | no | No full prompts or provider payloads |
| `token_usage` | object or null | no | Counts only when available |
| `completed_at` | string or null | no | Completion timestamp |

Validation rules:
- Invalid 001 output must not become an editable review session.
- LLM schema-validation failures may appear inside `output.validation_report`
  when the output remains reviewable.
- Full prompts, provider payloads, API keys, and raw secret material are not
  included.

### StructuringPipelineOutput

Canonical 001 draft output consumed by the workbench.

Key expectations:
- Contains extraction provenance, document draft, units, semantic draft fields,
  reference candidates, dependency graph, validation report, evidence, warnings,
  and review statuses.
- Frontend validation is a UI mirror only; Python/Pydantic 001 schema remains
  canonical.
- Must be immutable as `base_output` once a review session starts.

### ReviewSessionState

Client-side workbench state for one draft.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `session_id` | string | yes | Workbench session ID |
| `input_kind` | WorkbenchInputKind | yes | Markdown run or JSON replay |
| `source_markdown` | string or null | no | Present for Markdown flow |
| `source_output_ref` | SourceOutputRef | yes | Stable source reference |
| `base_output` | StructuringPipelineOutput | yes | Immutable 001 draft |
| `patches` | list[StructuringReviewPatch] | yes | Expert edits |
| `decisions` | list[StructuringReviewDecision] | yes | Expert decisions |
| `curation_records` | list[AssetCurationRecord] | yes | Expert notes |
| `review_gate_report` | ReviewGateReport | yes | Package readiness |
| `merged_output` | StructuringPipelineOutput | yes | Base plus patches |

Validation rules:
- `base_output` is never mutated.
- `merged_output` is review material only.
- Session state is not a persistence database.

### SourceOutputRef

Stable reference used by review artifacts.

| Field | Type | Required |
|-------|------|----------|
| `contract_version` | string | yes |
| `document_id` | string | yes |
| `source_id` | string | yes |
| `source_file` | string | yes |
| `loaded_at` | string | yes |
| `structuring_run_id` | string or null | no |

Hashes are not required for MVP.

### StructuringReviewPatch

Field-level expert edit against `base_output`.

Required fields:
- `source_output_ref`
- `target_type`
- `target_id`
- `unit_id`
- `field_path`
- `old_value`
- `new_value`
- `reviewer_note`
- `reviewer_decision`
- `reviewed_at`
- `reviewer_identity`

Validation rules:
- `old_value` must reflect `base_output`.
- Patches do not promote assets.
- Multiple edits to the same field must either be exported as a sequence or
  clearly consolidated.

### StructuringReviewDecision

Target-level expert decision.

Required fields:
- `source_output_ref`
- `target_type`
- `target_id`
- `unit_id`
- `reviewer_decision`
- `reviewer_note`
- `reviewed_at`
- `reviewer_identity`

Validation rules:
- Decisions can approve, reject, request changes, request more evidence, mark
  not applicable, or supersede a target.
- Required target decisions feed `ReviewGateReport`.

### ReviewGateReport

Computed readiness report for export status.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `status` | IntegratedPackageStatus | yes | `needs_review` or `reviewed_for_structuring` |
| `required_target_counts` | object | yes | Counts by target type |
| `completed_target_counts` | object | yes | Counts by target type |
| `blocking_validation_findings` | list[object] | yes | Error or unresolved findings |
| `remaining_review_reasons` | list[string] | yes | Human-readable blockers |

Validation rules:
- `reviewed_for_structuring` requires no blocking validation findings and all
  required targets decided.
- A reviewer can mark a target `not_applicable`, but the decision must be
  explicit and auditable.

### IntegratedStructuringReviewPackage

Export artifact for one reviewed workbench session.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `package_version` | string | yes | Workbench package contract version |
| `package_id` | string | yes | Workbench-generated package ID |
| `input_kind` | WorkbenchInputKind | yes | Markdown or JSON replay |
| `source_markdown` | string or null | no | Present for Markdown flow |
| `source_output_ref` | SourceOutputRef | yes | Base output reference |
| `base_output` | StructuringPipelineOutput | yes | Immutable 001 draft |
| `review_patches` | list[StructuringReviewPatch] | yes | Expert edits |
| `review_decisions` | list[StructuringReviewDecision] | yes | Expert decisions |
| `curation_records` | list[AssetCurationRecord] | yes | Expert notes |
| `merged_output` | StructuringPipelineOutput | yes | Patched reviewed output |
| `review_gate_report` | ReviewGateReport | yes | Readiness evidence |
| `package_status` | IntegratedPackageStatus | yes | Mirrors gate report |
| `exported_at` | string | yes | Timestamp |

Validation rules:
- `base_output` must remain unchanged.
- `merged_output` remains Admin review material.
- `reviewed_for_structuring` does not mean runtime-safe.
- Package must not include provider secrets, full prompts, or raw provider
  payloads.
