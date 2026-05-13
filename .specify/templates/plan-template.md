# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Answer each Arbiter constitution gate before design work proceeds:

- **Admin / Runtime Separation**: Classify the feature as Admin, Runtime,
  shared asset management, or cross-cutting infrastructure. If it crosses the
  boundary, name the reviewed asset handoff schema and review-status gate.
  Confirm Admin-side LLM-assisted regulation structuring remains draft-only
  until validation and human review.
- **Unified Model Access**: Confirm all model calls route through LLMClient /
  ModelProvider, with provider configuration outside business logic and mock
  provider coverage for tests.
- **Structured Data Contracts**: List every core JSON / Pydantic schema touched
  or introduced, including validation expectations for model outputs.
- **Temporal Regulation Basis**: Confirm regulation assets and runtime judgment
  drafts preserve source version, effective date, expiration date,
  amendment/source-version relation, and as-of-date basis where available.
- **Citation and Evidence**: Confirm judgment drafts cite stable regulation unit
  IDs, source document/version, article or clause number where available, and
  retrieval provenance; free-text citation labels are insufficient.
- **Runtime Review Gates**: Confirm Runtime rejects draft / needs_review /
  missing-review-status regulation assets unless execution mode is explicitly
  marked as test.
- **Secure Configuration**: Identify environment/config variables and confirm no
  real secrets, private scenarios, or internal rules are hard-coded.
- **Auditable but Sanitized Logging**: Define the IDs, validation results,
  errors, review status, temporal basis, retrieval provenance, and redaction
  strategy that traces/logs will capture.
- **Code Quality and Testability**: List required tests for schema validation,
  parsing or retrieval boundaries, temporal basis, citation provenance, runtime
  review-status gates, model-output validation, error paths, and
  security-sensitive behavior.

Any failed gate MUST be recorded in Complexity Tracking with a mitigation and
owner before implementation tasks are generated.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
