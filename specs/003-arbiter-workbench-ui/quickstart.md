# Quickstart: Arbiter Workbench UI

This quickstart describes the revised spec003 MVP validation target. It is a
planning artifact only; implementation code is not changed by this plan.

## Preconditions

- 001 `StructuringPipelineOutput` remains the canonical structuring output.
- The workbench uses a thin Admin structuring adapter to invoke 001 from
  Markdown.
- All model calls are routed through 001 `LLMClient / ModelProvider`.
- Tests use a mock provider; no real model call is required for MVP validation.
- PDF/Word parsing, 002 runtime execution, retrieval, rule execution, and asset
  promotion are outside scope.

## Expected Validation Flow

1. Start the local Admin structuring adapter with a mock `ModelProvider`.
2. Start the workbench UI.
3. Paste or upload Markdown with a title, chapter, articles, and at least one
   cross-reference.
4. Choose whether to use LLM-assisted parsing, then click the parse action.
5. Confirm the UI sends a `StructuringRunRequest` with the selected
   `llm_assisted` value and does not call a model provider directly.
6. Confirm the adapter returns a valid 001 `StructuringPipelineOutput` with
   `extraction_method = mixed` when mock LLM enrichment is accepted.
7. Confirm the review UI shows extraction provenance, document classification,
   temporal metadata, unit tree, semantic draft fields, evidence text,
   reference candidates, dependency edges, validation findings, and warnings.
8. Edit one semantic draft field and confirm a `StructuringReviewPatch` is
   recorded against immutable base output.
9. Approve or mark not applicable the required document, semantic draft,
   reference candidate, and dependency edge targets.
10. Confirm `ReviewGateReport` stays `needs_review` while any required target
    remains undecided or any blocking validation finding remains.
11. Confirm `ReviewGateReport` becomes `reviewed_for_structuring` only after
    required review gates are satisfied.
12. Export `IntegratedStructuringReviewPackage`.
13. Confirm export contains source Markdown, base output, merged output, review
    patches, review decisions, curation records, review gate report,
    extraction provenance, and package status.
14. Confirm export contains no active `RulePack`, formal `RuleItem`, final
    `JudgmentResult`, runtime-safe reviewed asset, final compliance conclusion,
    API key, full prompt, or raw provider payload.
15. Import an existing 001 JSON fixture and confirm it opens through the same
    review surfaces as an advanced replay path.

## Negative Checks

- Empty Markdown creates no structuring run.
- Adapter failure creates no editable review session.
- A selected LLM-assisted run with no configured provider creates a structured
  failure and no editable review session.
- Schema-invalid 001 output creates no editable review session.
- LLM schema-validation failures are visible as findings when output remains
  reviewable.
- The frontend contains no direct model provider calls and no provider secrets.
- `base_output` remains unchanged after edits.
- A package with unresolved review gates exports as `needs_review`, not
  `reviewed_for_structuring`.
- A `reviewed_for_structuring` package is still not runtime-safe and is not an
  active rule or final judgment.

## Suggested Commands

The eventual implementation should provide separate checks for frontend and
001 adapter behavior:

```bash
npm run test
npm run dev
PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring -q
```

Live LLM calls are not required for the MVP acceptance suite.
