# Quickstart: Regulation Structuring Pipeline

This quickstart describes how to validate the planned offline/admin pipeline
after implementation. It intentionally does not involve frontend UI,
ComplianceJudgmentAgent, JudgmentResult, active RulePack, formal RuleItem,
asset promotion, or production review workflows.

## 1. Install local test dependencies

```bash
./.venv/bin/python -m pip install -e .
```

## 2. Run the structuring test slice

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring -q
```

Expected result:
- Schema validation tests pass.
- Normalized text and Markdown intake tests pass.
- Optional FileInput -> ExtractedTextBundle -> NormalizedTextInput adapter
  boundary tests pass without OCR, password handling, or full layout recovery.
- Document classification draft tests pass.
- Temporal/version metadata extraction tests pass.
- Hierarchy/article splitting tests pass.
- Explicit unit tree fields support stable parent/order/display rendering.
- Reference candidate extraction tests pass.
- LLM-assisted extraction schema validation tests pass using a mock provider.
- Model provider boundary tests pass.
- Dependency graph draft tests pass.
- Validation report tests pass.
- JSON export and round-trip tests pass.
- Runtime boundary tests confirm no judgment-agent access.

## 3. Inspect fixture coverage

Fixture inputs cover:
- Markdown hierarchy.
- Normalized text hierarchy.
- External regulation and internal policy source-type classification.
- Extensible document category and topic tags.
- ReviewStatus enum values, with pipeline-created outputs always set to
  `needs_review`.
- Ambiguous references.
- LLM-assisted semantic extraction outputs with evidence, confidence, and
  ambiguity notes.
- Scenario-oriented semantic draft fields such as trigger events, required and
  prohibited actions, deadlines, thresholds, subject/object scope, and reporting
  obligations.
- Schema-invalid LLM outputs that must become validation findings or structured
  errors.
- Proposed dependency edges, cross-document target labels, and unresolved graph
  issues.
- Duplicate article labels.
- Missing status/date/version/amendment metadata.
- Extraction provenance with bounded method and trace identifiers.

No fixture requires real model calls, secrets, databases, UI, or runtime agent
tools. LLM-assisted behavior is exercised through mock provider outputs.

## 4. Verify exported JSON

After implementation, run the planned export path against fixture inputs and
inspect the JSON output manually. The output must include:
- `RegulationDocumentDraft` with `parse_status = needs_review`.
- Temporal metadata with version/amendment/validity context when available, and
  nulls or ambiguity notes when unavailable.
- `DocumentClassificationDraft` with `review_status = needs_review` and
  extensible tags.
- `RegulationUnitDraft` entries whose `semantic_draft` and unit-level
  `review_status` values are both `needs_review`, with `parent_unit_id`,
  `order_index`, and `display_label` for stable review rendering.
- `SemanticUnitDraft` entries may include trigger events, required actions,
  prohibited actions, deadlines, thresholds, subject scope, object scope, and
  reporting obligations, all draft-only and evidence-backed where applicable.
- `ReferenceCandidate` entries for textual reference clues.
- `RegulationUnitRelationDraft` / `DependencyEdgeDraft` entries for proposed
  resolved dependency edges, including cross-document target metadata when
  available.
- `ResolvedDependencyGraphDraft` with candidates and proposed edges separated.
- `StructuringValidationReport` with warnings for deterministic parsing,
  LLM extraction validation, temporal ambiguity, tree/provenance gaps, semantic
  draft issues, and dependency graph issues.
- `ExtractionProvenance` with `extraction_method`, optional
  `prompt_contract_version`, and optional `model_trace_id`, without secrets,
  full prompts, or unnecessary raw sensitive text.

The output must not include JudgmentResult, active RulePack, formal RuleItem,
final compliance conclusions, runtime agent answers, or runtime-safe reviewed
assets. `StructuringPipelineOutput` remains a draft bundle for a later
review/promotion workflow.
