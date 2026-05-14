# Contract: Arbiter Workbench UI

**Contract status**: Frontend/Admin adapter planning contract
**Scope**: Markdown-to-001 LLM-assisted structuring, expert review, integrated package export
**Out of scope**: direct frontend model calls, PDF/DOCX parsing, 002 Agent
Runtime execution, retrieval, vector search, rule execution, active `RulePack`,
formal `RuleItem`, final `JudgmentResult`, final compliance conclusions,
production identity management, and database persistence.

## Workbench-to-001 Structuring Run

The workbench triggers LLM-assisted parsing through an Admin-only adapter. The
adapter delegates to the 001 Regulation Structuring Pipeline and returns a
validated 001 output.

### StructuringRunRequest

```json
{
  "request_id": "req-001",
  "input": {
    "input_kind": "markdown",
    "source_id": "src-policy-001",
    "source_file": "investment-policy.md",
    "raw_markdown": "# 投资管理制度\n\n第一条 公司对外投资应履行审批程序。",
    "source_type": "internal_policy",
    "metadata": {
      "title": "投资管理制度",
      "document_number": null,
      "effective_date": null,
      "issuer_name": null,
      "topic_tags": ["investment"]
    }
  },
  "llm_assisted": true,
  "model_mode": "configured_provider",
  "requested_at": "2026-05-14T00:00:00Z"
}
```

Required behavior:
- Frontend must not include provider API keys, base URLs, raw provider payloads,
  or model-specific secrets.
- Adapter converts this request into 001 `NormalizedTextInput`.
- `llm_assisted=true` authorizes only the Admin adapter/001 pipeline to use the
  configured `ModelProvider`.
- Empty Markdown is rejected before adapter execution when possible.

### StructuringRunResult

```json
{
  "request_id": "req-001",
  "run_id": "struct-run-001",
  "status": "succeeded",
  "output": {
    "contract_version": "v1",
    "extraction_provenance": {
      "extraction_method": "mixed",
      "prompt_contract_version": "structuring-v1",
      "model_trace_id": "trace-llm"
    },
    "document": {},
    "units": [],
    "reference_candidates": [],
    "dependency_graph": {},
    "validation_report": {}
  },
  "errors": [],
  "warnings": [],
  "sanitized_trace": {
    "adapter": "001-structuring",
    "model_call_count": 3,
    "redaction_warnings": []
  },
  "token_usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  },
  "completed_at": "2026-05-14T00:00:20Z"
}
```

Required behavior:
- `output` must validate as 001 `StructuringPipelineOutput`.
- Invalid output creates `status = validation_failed` and no editable review
  session.
- LLM schema-validation findings may appear in `output.validation_report` when
  the output is still reviewable.
- `sanitized_trace` must not include full prompts, provider payloads, API keys,
  or unnecessary sensitive raw text.

## JSON Replay Import

The workbench may import existing 001 `StructuringPipelineOutput` JSON.

Required behavior:
- Treat this as advanced replay/fixture input, not the main MVP user path.
- Validate the loaded shape before creating a review session.
- Preserve imported output as immutable `base_output`.
- Display provenance and validation findings exactly as supplied.

## Review Surface Contract

The workbench must display these 001 output areas:

- `extraction_provenance`
- document metadata and `DocumentClassificationDraft`
- temporal metadata
- ordered unit tree
- unit source text, normalized text, source location, and hierarchy
- full `SemanticUnitDraft`
- `ReferenceCandidate[]`
- `DependencyEdgeDraft[]`
- `StructuringValidationReport`
- warnings and review statuses

Missing values are shown as incomplete. The UI must not fabricate fields.

## Review Artifacts

### StructuringReviewPatch

```json
{
  "source_output_ref": {
    "contract_version": "v1",
    "document_id": "doc-001",
    "source_id": "src-policy-001",
    "source_file": "investment-policy.md",
    "loaded_at": "2026-05-14T00:00:20Z",
    "structuring_run_id": "struct-run-001"
  },
  "target_type": "semantic_draft",
  "target_id": "unit-001.semantic_draft.summary",
  "unit_id": "unit-001",
  "field_path": "semantic_draft.summary",
  "old_value": "draft summary",
  "new_value": "reviewed summary",
  "reviewer_note": "Adjusted wording against source text.",
  "reviewer_decision": "needs_changes",
  "reviewed_at": "2026-05-14T00:10:00Z",
  "reviewer_identity": null
}
```

Required behavior:
- `old_value` is from immutable `base_output`.
- `new_value` applies only to merged output.
- Patch export must not duplicate full raw source unless the edited field
  itself is source text.

### StructuringReviewDecision

```json
{
  "source_output_ref": {
    "contract_version": "v1",
    "document_id": "doc-001",
    "source_id": "src-policy-001",
    "source_file": "investment-policy.md",
    "loaded_at": "2026-05-14T00:00:20Z",
    "structuring_run_id": "struct-run-001"
  },
  "target_type": "dependency_edge",
  "target_id": "edge-001",
  "unit_id": "unit-001",
  "reviewer_decision": "approved",
  "reviewer_note": "Cross-reference is supported by source text.",
  "reviewed_at": "2026-05-14T00:12:00Z",
  "reviewer_identity": null
}
```

Allowed `target_type` values:
- `document`
- `unit`
- `semantic_draft`
- `reference_candidate`
- `dependency_edge`
- `curation_note`

Allowed `reviewer_decision` values:
- `approved`
- `rejected`
- `needs_changes`
- `needs_more_evidence`
- `not_applicable`
- `superseded`

## ReviewGateReport

```json
{
  "status": "needs_review",
  "required_target_counts": {
    "document": 1,
    "semantic_draft": 10,
    "reference_candidate": 2,
    "dependency_edge": 1
  },
  "completed_target_counts": {
    "document": 1,
    "semantic_draft": 9,
    "reference_candidate": 2,
    "dependency_edge": 1
  },
  "blocking_validation_findings": [],
  "remaining_review_reasons": [
    "1 semantic draft target still requires an explicit review decision."
  ]
}
```

Required behavior:
- Status is `reviewed_for_structuring` only when no blocking findings remain
  and required targets are decided.
- Review gates are visible before export.
- `reviewed_for_structuring` remains Admin-only and not runtime-safe.

## IntegratedStructuringReviewPackage

```json
{
  "package_version": "v1",
  "package_id": "pkg-001",
  "input_kind": "markdown",
  "source_markdown": "# 投资管理制度\n\n第一条 公司对外投资应履行审批程序。",
  "source_output_ref": {
    "contract_version": "v1",
    "document_id": "doc-001",
    "source_id": "src-policy-001",
    "source_file": "investment-policy.md",
    "loaded_at": "2026-05-14T00:00:20Z",
    "structuring_run_id": "struct-run-001"
  },
  "base_output": {},
  "review_patches": [],
  "review_decisions": [],
  "curation_records": [],
  "merged_output": {},
  "review_gate_report": {
    "status": "reviewed_for_structuring",
    "remaining_review_reasons": []
  },
  "package_status": "reviewed_for_structuring",
  "exported_at": "2026-05-14T00:20:00Z"
}
```

Required behavior:
- Preserve immutable base output.
- Apply review patches only to merged output.
- Include source Markdown for Markdown-origin sessions.
- Include extraction provenance from 001.
- Do not include secrets, full prompts, raw provider payloads, active rules, or
  final judgments.
- Do not claim runtime-safe reviewed status.
