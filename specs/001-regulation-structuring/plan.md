# Implementation Plan: Regulation Structuring Pipeline

**Branch**: `001-regulation-structuring` | **Date**: 2026-05-13 | **Spec**: `specs/001-regulation-structuring/spec.md`
**Input**: Feature specification from `/specs/001-regulation-structuring/spec.md`

## Summary

Build an offline/admin Regulation Structuring Pipeline that turns normalized
text or Markdown from external regulations and internal policies into
schema-backed, reviewable draft JSON. The pipeline uses a hybrid strategy:
deterministic code owns intake, source preservation, obvious structural hints,
stable source_id / document_id linkage, JSON serialization, schema validation,
and validation reports, while
LLM-assisted extraction handles variable-format hierarchy interpretation,
semantic unit extraction, article/paragraph boundary proposals, document
classification, definitions, obligations, exceptions, actors, conditions,
applicability, reference candidates, and draft dependency edges.

All model calls go through `LLMClient` / `ModelProvider`; all model outputs are
validated through Pydantic schemas before entering the output bundle. Every
semantic field remains draft-only with `review_status = needs_review`, and the
pipeline must not output `JudgmentResult`, formal `RuleItem`, active `RulePack`,
or final compliance conclusions. The pipeline is not exposed as a
`ComplianceJudgmentAgent` tool.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: Pydantic schemas, existing `LLMClient` /
`ModelProvider` abstraction, pytest with mock model provider fixtures  
**Storage**: File-based JSON draft artifacts; no production database in this
feature  
**Testing**: pytest unit and integration-style fixture tests  
**Target Platform**: Local or controlled server-side admin workflow  
**Project Type**: Python library/admin pipeline with optional CLI-style entry
points  
**Performance Goals**: Process representative policy/regulation fixture
documents deterministically enough for review; no live-model latency target in
this first slice  
**Constraints**: Offline/admin only, no direct runtime judgment integration, no
real model calls in unit tests, no secrets or provider settings hard-coded in
business logic, schema-invalid LLM output must become validation findings or
structured errors  
**Scale/Scope**: Single-document first slice with support for cross-document
target metadata in draft dependency edges; production review workflow and asset
promotion are out of scope

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Admin / Runtime Separation**: PASS. This is an Admin-only structuring
  pipeline. It prepares draft assets and validation findings, but does not
  parse raw files in Runtime, does not expose a `ComplianceJudgmentAgent` tool,
  and does not produce runtime judgment evidence. Later handoff must go through
  reviewed assets, not these draft outputs directly.
- **Unified Model Access**: PASS. LLM-assisted extraction is allowed, but every
  call must route through `LLMClient` / `ModelProvider`; provider configuration
  stays outside business logic, and tests use a mock provider.
- **Structured Data Contracts**: PASS. Core outputs are JSON/Pydantic-backed:
  `NormalizedTextInput`, `RegulationDocumentDraft`,
  `DocumentClassificationDraft`, `RegulationUnitDraft`, `SemanticUnitDraft`,
  `ReferenceCandidate`, `DependencyEdgeDraft` /
  `RegulationUnitRelationDraft`, `ResolvedDependencyGraphDraft`,
  `StructuringValidationReport`, and `StructuringPipelineOutput`. LLM outputs
  must validate against these schemas before entering downstream output.
- **Secure Configuration**: PASS. Model settings and secrets are read through
  the existing model/config boundary and are not serialized into artifacts.
  Source labels must not require absolute local paths.
- **Auditable but Sanitized Logging**: PASS. Logs/traces may capture document
  IDs, unit IDs, validation results, model-output validation failures, review
  status, and bounded evidence snippets; they must not capture secrets, provider
  payloads, full prompts, absolute local paths, or unnecessary raw sensitive
  text.
- **Code Quality and Testability**: PASS. Required tests cover schemas,
  normalized text/Markdown intake, hybrid extraction boundaries, mock-provider
  LLM validation, validation reports, JSON round trips, and the negative runtime
  boundary.

No gate violations are accepted for this plan.

## Project Structure

### Documentation (this feature)

```text
specs/001-regulation-structuring/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── structuring-pipeline-contract.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)
```text
src/
└── arbiter/
    ├── schemas/
    │   └── regulation_structuring.py
    └── structuring/
        ├── intake.py
        ├── extraction.py
        ├── llm_extraction.py
        ├── pipeline.py
        ├── validation.py
        └── export.py

tests/
└── structuring/
    ├── fixtures/
    ├── conftest.py
    ├── test_regulation_structuring_schemas.py
    ├── test_regulation_structuring_roundtrip.py
    ├── test_intake.py
    ├── test_structure_first_splitting.py
    ├── test_regulation_structuring_pipeline.py
    ├── test_llm_structuring_validation.py
    ├── test_traceable_units.py
    ├── test_unit_tree.py
    ├── test_temporal_metadata.py
    ├── test_structuring_validation_report.py
    ├── test_reference_dependency_graph.py
    ├── test_semantic_unit_draft.py
    ├── test_review_status_boundaries.py
    └── test_structuring_runtime_boundary.py
```

**Structure Decision**: Keep the feature in an Admin-side `arbiter.structuring`
package and schema module. Do not add code under runtime judgment, agent tools,
web UI, production storage, or active rule-pack loaders for this feature.

## Phase 0 Research

Completed in `specs/001-regulation-structuring/research.md`.

Key decisions:
- Use hybrid deterministic + LLM-assisted extraction.
- Accept normalized text and Markdown as the first direct input boundary.
- Define Pydantic schemas before parser and model behavior.
- Keep validation reports as primary output.
- Use file-based, schema-backed JSON export.
- Keep `JudgmentResult`, active `RulePack`, formal `RuleItem`, unvalidated LLM
  output, final legal judgment, and runtime agent answers out of scope.

## Phase 1 Design & Contracts

Completed artifacts:
- `specs/001-regulation-structuring/data-model.md`
- `specs/001-regulation-structuring/contracts/structuring-pipeline-contract.md`
- `specs/001-regulation-structuring/quickstart.md`

The contract defines `structure_regulation(input) -> StructuringPipelineOutput`
as an offline/admin operation. The output is reviewable draft JSON containing a
document draft, unit drafts, reference candidates, a dependency graph draft, and
a validation report.

## Post-Design Constitution Check

PASS. The design artifacts preserve Admin/Runtime separation, route all model
calls through `LLMClient` / `ModelProvider`, constrain model output with
schemas, keep semantic extraction draft-only, define sanitized audit behavior,
and include planned tests for model-output validation and runtime-boundary
negative cases.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
