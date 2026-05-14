# Implementation Plan: Arbiter Workbench UI

**Branch**: `003-arbiter-workbench-ui` | **Date**: 2026-05-14 | **Spec**: `specs/003-arbiter-workbench-ui/spec.md`
**Input**: Feature specification from `/specs/003-arbiter-workbench-ui/spec.md`

## Summary

Revise spec003 from a JSON/fixture review UI into an Admin-side workbench where
the primary flow is Markdown input -> click LLM-assisted parse -> 001
`StructuringPipelineOutput` draft -> expert review and revision ->
integrated reviewed-for-structuring package export.

The workbench must not call model providers directly. It needs a thin Admin
structuring adapter that accepts Markdown as `StructuringRunRequest`, delegates
to the canonical 001 pipeline, and returns `StructuringRunResult` containing a
validated `StructuringPipelineOutput`, structured errors, sanitized trace
summary, and optional token usage. JSON import remains only an advanced replay
or fixture path.

## Technical Context

**Language/Version**: TypeScript 5.x browser workbench; Python 3.11/Pydantic 001 pipeline and schemas
**Primary Dependencies**: Vite, React, Zod frontend validation mirror, Python Admin structuring adapter delegating to `arbiter.structuring.pipeline.structure_regulation`, `LLMClient / ModelProvider` for all model calls
**Storage**: In-memory review session plus explicit JSON export artifacts; no database in MVP
**Testing**: Vitest contract/unit tests, Playwright smoke tests, pytest tests for 001 adapter contract and mock `ModelProvider` behavior
**Target Platform**: Local controlled Admin environment
**Project Type**: Cross-surface Admin web workbench plus local Admin structuring adapter
**Performance Goals**: One Markdown document at a time; representative 10+ unit documents remain navigable without visible tree ordering mismatches
**Constraints**: No frontend direct LLM calls; no PDF/DOCX parsing; no 002 runtime execution; no retrieval/vector search/rule execution; no active `RulePack`; no formal `RuleItem`; no final compliance conclusion; secrets never appear in frontend source, fixtures, logs, or exports
**Scale/Scope**: MVP covers Markdown-to-LLM-assisted 001 draft generation, expert review of core 001 fields, package export, and JSON replay import

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Admin / Runtime Separation**: PASS. This is Admin-side structuring review.
  It may produce draft and `reviewed_for_structuring` packages, but those are
  not runtime-safe reviewed assets and cannot be used by 002 as formal judgment
  evidence.
- **Unified Model Access**: PASS. The UI invokes an Admin structuring adapter;
  model calls remain inside 001 via `LLMClient / ModelProvider`. Frontend code
  must not contain provider SDK calls, base URLs, model names, or API keys.
- **Structured Data Contracts**: PASS. Core contracts are
  `StructuringRunRequest`, `StructuringRunResult`,
  `StructuringPipelineOutput`, `StructuringReviewPatch`,
  `StructuringReviewDecision`, `AssetCurationRecord`,
  `ReviewGateReport`, and `IntegratedStructuringReviewPackage`.
- **Temporal Regulation Basis**: PASS. 001 temporal metadata is displayed and
  preserved; missing temporal basis is shown as incomplete.
- **Citation and Evidence**: PASS. Source locations, evidence text, reference
  candidates, dependency edges, validation findings, and extraction provenance
  are first-class review surfaces.
- **Runtime Review Gates**: PASS. Runtime placeholders must reject or block
  `needs_review` structuring packages outside test mode.
- **Secure Configuration**: PASS. Provider configuration stays server/admin-side
  and environment-driven. The frontend never receives secrets.
- **Auditable but Sanitized Logging**: PASS. Adapter responses may include
  sanitized trace summaries, IDs, status, validation findings, and token counts,
  but not full prompts, provider payloads, API keys, or unnecessary raw content.
- **Code Quality and Testability**: PASS. Required tests cover structuring
  adapter request/response contracts, mock provider behavior, frontend no-direct
  model-call boundary, draft display, review gate behavior, integrated export,
  and base-output immutability.

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
└── tasks.md
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── adapters/          # frontend adapter clients, no direct model calls
│   ├── contracts/         # Zod UI and package contracts
│   ├── workbench/         # review UI and session state
│   └── validation/
└── tests/

src/arbiter/
├── schemas/
│   └── regulation_structuring.py
├── structuring/
│   ├── pipeline.py        # canonical 001 structuring pipeline
│   └── llm_extraction.py  # 001 LLM-assisted enrichment
└── llm/                   # shared ModelProvider boundary

tests/
└── structuring/
```

**Structure Decision**: 003 owns the UI, review state, and integrated package
contract. 001 remains the canonical owner of structuring schemas and
LLM-assisted extraction. A thin Admin adapter boundary is required between them
because the browser UI cannot call Python pipeline code directly.

## Phase 0 Research

Completed in `specs/003-arbiter-workbench-ui/research.md`.

Key decisions:
- Replace UI-local Markdown conversion as the primary path with a real
  Admin-only 001 structuring adapter.
- Keep JSON import as an advanced replay/debug path.
- Display 001 LLM-assisted output surfaces that are currently missing from the
  UI: extraction provenance, full classification details, reference candidates,
  dependency edges, validation findings, and review gates.
- Export packages as `needs_review` or `reviewed_for_structuring`, never as
  runtime-safe assets.
- Keep model access out of the frontend and inside 001's `ModelProvider`
  boundary.

## Phase 1 Design & Contracts

Completed artifacts:
- `specs/003-arbiter-workbench-ui/data-model.md`
- `specs/003-arbiter-workbench-ui/contracts/workbench-ui-contracts.md`
- `specs/003-arbiter-workbench-ui/quickstart.md`

The design defines the workbench-to-001 adapter request/response, review gate
state, integrated package export, JSON replay path, and future-runtime
boundary. It does not define active rule promotion, final compliance judgments,
retrieval, vector search, PDF/DOCX parsing, or production user management.

## Post-Design Constitution Check

PASS. The Phase 1 artifacts preserve Admin/Runtime separation, route model
calls through 001/ModelProvider only, keep all handoffs schema-backed, preserve
temporal/evidence/provenance fields, and make review gates explicit before any
package can be marked `reviewed_for_structuring`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Local Admin adapter boundary | Browser UI must trigger 001 LLM-assisted structuring from Markdown | JSON-only import forces users to run 001 outside the UI and misses the target workflow |
