# Implementation Plan: Arbiter Workbench UI

**Branch**: `003-arbiter-workbench-ui` | **Date**: 2026-05-13 | **Spec**: `specs/003-arbiter-workbench-ui/spec.md`
**Input**: Feature specification from `/specs/003-arbiter-workbench-ui/spec.md`

## Summary

Build a frontend-only Arbiter Workbench that first supports expert curation of
001 `StructuringPipelineOutput` JSON and second prepares mocked or future 002
runtime-facing screens. The plan is contract-first: load fixture/exported JSON,
validate and display reviewable document metadata and unit data, export separate
review and curation artifacts, and render placeholder runtime scenario,
judgment, citation, evidence, and sanitized trace views through mock/future
adapters only.

No part of this feature implements 001 structuring, 002 Agent Runtime,
retrieval, vector search, rule execution, LLM calls, active `RulePack`, formal
`RuleItem`, final `JudgmentResult`, PDF/DOCX parsing, or final compliance
conclusions.

## Technical Context

**Language/Version**: TypeScript 5.x browser workbench; Python 3.11/Pydantic 001 contracts remain the canonical source reference for fixture compatibility  
**Primary Dependencies**: Vite, React, Zod frontend validation mirror for loaded JSON, browser file import/export, fixture-based mocked runtime adapter  
**Storage**: Local in-memory session state plus explicit JSON export artifacts; no database or backend persistence in this feature  
**Testing**: Vitest frontend contract tests, fixture-load tests, export artifact tests, and Playwright UI smoke tests using mocked data  
**Target Platform**: Local browser-based expert workbench in a controlled development/admin environment  
**Project Type**: Frontend application added alongside the existing Python contract package  
**Performance Goals**: Load and navigate representative fixture outputs with at least 10 regulation units without visible ordering or parent/child mismatches  
**Constraints**: Frontend-only; no direct LLM calls; no 001 pipeline execution; no 002 runtime dependency; no retrieval/vector search/rule execution; no raw PDF/DOCX parsing; no asset promotion  
**Scale/Scope**: MVP covers one loaded `StructuringPipelineOutput` at a time, exported review/curation artifacts, and mocked runtime-facing views

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Admin / Runtime Separation**: PASS. This is a cross-surface frontend
  workbench, but implementation is limited to Admin data-asset curation and
  placeholder runtime-facing display. Handoff artifacts are
  `StructuringReviewPatch`, `StructuringReviewDecision`, and
  `AssetCurationRecord`; none become reviewed runtime assets or formal rules.
- **Unified Model Access**: PASS. The feature makes no model calls. It may
  display LLM-derived draft fields already present in 001 outputs, but it does
  not call `LLMClient`, providers, or direct vendor APIs.
- **Structured Data Contracts**: PASS. Core contracts are
  `StructuringPipelineOutput`, `SourceOutputRef`, `StructuringReviewPatch`,
  `StructuringReviewDecision`, `AssetCurationRecord`,
  `RuntimeScenarioInput`, `RuntimeJudgmentDraftView`,
  `RuntimeCitationView`, `RuntimeEvidenceView`, and `RuntimeTraceView`.
  Any frontend Zod validation for loaded `StructuringPipelineOutput` JSON is a
  UI validation mirror only; the canonical 001 schema remains the existing
  Python/Pydantic contract.
- **Temporal Regulation Basis**: PASS. Review and runtime-facing views preserve
  source version, effective date, expiration date, amendment/source-version
  relation, and as-of-date basis when present, and show missing facts as
  incomplete rather than inferred.
- **Citation and Evidence**: PASS. Runtime citation placeholders require stable
  regulation unit IDs, source document/version, article or clause number where
  available, adapter-provided provenance, and as-of-date basis. Free-text-only
  citations are flagged as incomplete.
- **Runtime Review Gates**: PASS. This feature does not execute runtime logic.
  Placeholder runtime outputs are always drafts and are driven by mocked or
  future adapters only.
- **Secure Configuration**: PASS. No secrets or provider configuration are
  required. Fixtures and mock responses must not contain real private
  scenarios, API keys, provider payloads, or internal production rules.
- **Auditable but Sanitized Logging**: PASS. Export artifacts capture IDs,
  source references, reviewer decisions, timestamps, validation status, and
  notes. Runtime trace views show sanitized summaries only and block secrets,
  full prompts, provider payloads, and unnecessary sensitive raw text.
- **Code Quality and Testability**: PASS. Required tests cover fixture
  validation, document metadata review display, unit tree ordering, field-edit
  patch export, same-field unsaved edit export behavior, review decision
  targets, curation records, placeholder runtime contracts, incomplete citation
  handling, and trace redaction.

## Project Structure

### Documentation (this feature)

```text
specs/003-arbiter-workbench-ui/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── workbench-ui-contracts.md
├── checklists/
│   └── requirements.md
└── tasks.md             # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
frontend/
├── package.json
├── src/
│   ├── contracts/
│   ├── fixtures/
│   ├── adapters/
│   ├── workbench/
│   └── validation/
└── tests/
    ├── contract/
    ├── fixtures/
    └── smoke/

src/
└── arbiter/
    └── schemas/
        └── regulation_structuring.py   # Existing 001 contract reference

tests/
└── structuring/                         # Existing 001 tests, not owned by 003
```

**Structure Decision**: Add a frontend-only workbench under `frontend/` while
leaving 001 Python schema and pipeline implementation under `src/arbiter/` and
`tests/structuring/`. 003 may read fixture JSON shaped by 001, but it must not
modify or depend on running the 001 pipeline.

## Phase 0 Research

Completed in `specs/003-arbiter-workbench-ui/research.md`.

Key decisions:
- Keep the MVP frontend-only and file/fixture based.
- Treat 001 `StructuringPipelineOutput` as an imported contract, not a pipeline
  execution dependency.
- Export review and curation artifacts separately from source JSON.
- Make same-field unsaved edit export behavior explicit.
- Use mocked/future adapters for runtime-facing UI surfaces only.
- Keep placeholder runtime contracts explicitly non-final and replaceable until
  002 exists.

## Phase 1 Design & Contracts

Completed artifacts:
- `specs/003-arbiter-workbench-ui/data-model.md`
- `specs/003-arbiter-workbench-ui/contracts/workbench-ui-contracts.md`
- `specs/003-arbiter-workbench-ui/quickstart.md`

The design defines review/curation artifacts and placeholder runtime UI
contracts. It does not define backend endpoints, database tables,
authentication, retrieval, runtime execution, API routes, or final judgment
schemas.

## Post-Design Constitution Check

PASS. The Phase 1 artifacts preserve Admin/Runtime separation, avoid model
calls, keep review and curation artifacts separate from promoted assets,
represent all handoffs as explicit JSON-compatible contracts, keep runtime UI
contracts replaceable, and require sanitized runtime trace display.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
