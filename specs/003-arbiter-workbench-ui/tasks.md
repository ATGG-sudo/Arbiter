# Tasks: Arbiter Workbench UI

**Input**: Design documents from `/specs/003-arbiter-workbench-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Required for this feature because the spec requires contract validation, Admin/Runtime boundary checks, fixture loading, citation provenance, sanitized trace display, and invalid-input error paths.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files or has no dependency on another pending task
- **[Story]**: User story label, for example [US1], [US2], [US3]
- Include exact file paths in every task description

## Boundary Rules

- 003 tasks modify `frontend/` and `specs/003-arbiter-workbench-ui/` only.
- 003 may consume the 001 workbench invocation contract, but must not reimplement
  001 pipeline behavior, prompt logic, schema validation, or model-provider
  access.
- Do not modify `specs/001-regulation-structuring/` or
  `src/arbiter/schemas/regulation_structuring.py` from 003 tasks; any 001 adapter
  implementation is owned by spec001 tasks.
- Do not implement 002 Agent Runtime, retrieval, vector search, rule execution,
  direct LLM calls, database persistence, active `RulePack`, formal `RuleItem`,
  final `JudgmentResult`, or PDF/DOCX parsing.
- Runtime-facing flows remain mocked/future-adapter UI flows only.
- Frontend Zod validation is a UI mirror for adapter responses and replay JSON;
  the canonical 001 contract remains Python/Pydantic.
- Markdown intake must create `StructuringRunRequest` and invoke the Admin
  structuring adapter. JSON import remains an advanced replay/fixture path, not
  the primary MVP path.

## Phase 1: Setup

**Purpose**: Establish the Vite + React + TypeScript workbench surface and
frontend adapter-client workspace for 003.

- [ ] T001 Create frontend project directories in `frontend/src/contracts/`, `frontend/src/fixtures/`, `frontend/src/adapters/`, `frontend/src/workbench/`, `frontend/src/validation/`, `frontend/tests/contract/`, `frontend/tests/fixtures/`, and `frontend/tests/smoke/`
- [ ] T002 Create Vite React TypeScript package configuration in `frontend/package.json`
- [ ] T003 [P] Configure TypeScript for the frontend app in `frontend/tsconfig.json`
- [ ] T004 [P] Configure Vite for the frontend app in `frontend/vite.config.ts`
- [ ] T005 [P] Configure Vitest and Testing Library setup in `frontend/vitest.config.ts` and `frontend/tests/setup.ts`
- [ ] T006 [P] Configure Playwright smoke test project in `frontend/playwright.config.ts`
- [ ] T007 Create the React application entry files in `frontend/src/main.tsx`, `frontend/src/App.tsx`, and `frontend/src/styles.css`

---

## Phase 2: Foundational Contracts And Fixtures

**Purpose**: Define shared frontend contracts, fixtures, mock adapter boundaries, and safety utilities that block all user stories.

**CRITICAL**: No user story work should begin until frontend contracts and fixture validation exist.

- [X] T008 [P] Write contract tests for `StructuringRunRequest`, `StructuringRunResult`, and the `StructuringPipelineOutput` frontend validation mirror in `frontend/tests/contract/structuringOutput.contract.test.ts`
- [ ] T009 [P] Write contract tests for `StructuringReviewPatch`, `StructuringReviewDecision`, and `AssetCurationRecord` exports in `frontend/tests/contract/reviewArtifacts.contract.test.ts`
- [ ] T010 [P] Write contract tests for placeholder runtime UI contracts in `frontend/tests/contract/runtimeContracts.contract.test.ts`
- [X] T011 [P] Write targeted boundary tests for forbidden direct provider SDK calls, embedded model/base-url/API-key configuration, 002 runtime calls, backend/database files, and forbidden modifications to 001-owned paths in `frontend/tests/contract/scopeBoundary.contract.test.ts`
- [X] T012 Implement `StructuringRunRequest`, `StructuringRunResult`, and the `StructuringPipelineOutput` Zod frontend validation mirror in `frontend/src/contracts/structuringOutput.ts`
- [ ] T013 Implement review and curation artifact contracts in `frontend/src/contracts/reviewArtifacts.ts`
- [ ] T013a Implement `IntegratedStructuringReviewPackage` and input-kind contracts in `frontend/src/contracts/reviewArtifacts.ts`
- [ ] T014 Implement placeholder runtime UI contracts in `frontend/src/contracts/runtimeContracts.ts`
- [ ] T015 [P] Add a valid 10-unit `StructuringPipelineOutput` fixture in `frontend/src/fixtures/structuring-output.valid.json`
- [ ] T016 [P] Add invalid and schema-incompatible input fixtures in `frontend/src/fixtures/structuring-output.invalid.json`
- [ ] T017 [P] Add mocked runtime draft response fixtures in `frontend/src/fixtures/runtime-draft.mock.json`
- [ ] T018 Implement immutable loaded-source session state helpers in `frontend/src/workbench/sessionState.ts`
- [ ] T019 Implement JSON import validation helpers that create no editable session for invalid input in `frontend/src/validation/loadStructuringOutput.ts`
- [ ] T020 Implement sanitized trace redaction helpers in `frontend/src/validation/redaction.ts`
- [ ] T021 Implement review artifact export helpers without mutating immutable `base_output` in `frontend/src/workbench/exportArtifacts.ts`
- [X] T021a Implement the frontend Admin structuring adapter client in `frontend/src/adapters/adminStructuringAdapter.ts`; it sends `StructuringRunRequest`, accepts `StructuringRunResult`, and never calls model providers directly
- [ ] T021b Implement integrated package export helpers that preserve base output and apply edits only to `merged_output` in `frontend/src/workbench/exportArtifacts.ts`
- [ ] T022 Implement a mocked runtime adapter with no external calls in `frontend/src/adapters/mockRuntimeAdapter.ts`

**Checkpoint**: Frontend contracts, replay fixtures, Admin adapter client, mock runtime adapter, and boundary guards are ready.

---

## Phase 3: User Story 1 - Curate Reviewed Regulation Data Assets (Priority: P1) MVP

**Goal**: Experts can paste or upload Markdown, trigger 001 LLM-assisted
structuring through the Admin adapter, or load 001-compatible replay JSON,
inspect document and unit data, edit semantic draft fields, record
notes/decisions, and export an integrated modified structuring review package
without mutating base output.

**Independent Test**: Enter Markdown with a title, chapter, and article; verify
the UI sends `StructuringRunRequest` to the Admin adapter client and opens the
returned `StructuringPipelineOutput`; inspect the generated unit tree and
document metadata; select units; edit a semantic field; add a curation note;
export an integrated package; and verify `base_output` remains unchanged while
`merged_output` contains the reviewed edit. Repeat with
`frontend/src/fixtures/structuring-output.valid.json` to verify replay JSON still
opens through the same review surfaces.

### Tests for User Story 1

- [ ] T023 [P] [US1] Write fixture load and invalid-input tests in `frontend/tests/fixtures/structuringOutputLoad.test.ts`
- [ ] T024 [P] [US1] Write unit tree ordering and parent-child rendering tests in `frontend/tests/contract/unitTree.contract.test.ts`
- [ ] T025 [P] [US1] Write document metadata review tests in `frontend/tests/contract/documentMetadata.contract.test.ts`
- [ ] T026 [P] [US1] Write review patch, decision, curation note, and repeated-edit export tests in `frontend/tests/contract/reviewExport.contract.test.ts`
- [X] T026a [P] [US1] Write Admin adapter client and integrated package export tests in `frontend/tests/contract/integratedPackage.contract.test.ts`
- [ ] T027 [P] [US1] Write Playwright smoke test for the curation review flow in `frontend/tests/smoke/curation-flow.spec.ts`

### Implementation for User Story 1

- [X] T028 [US1] Implement Markdown run-request creation, Admin adapter invocation, and replay JSON loading UI in `frontend/src/workbench/StructuringOutputLoader.tsx`
- [ ] T029 [US1] Implement readable validation and adapter failure display for invalid inputs or failed `StructuringRunResult` values in `frontend/src/workbench/ValidationFailurePanel.tsx`
- [ ] T030 [US1] Implement document metadata review surface in `frontend/src/workbench/DocumentMetadataPanel.tsx`
- [ ] T031 [US1] Implement unit tree display using `parent_unit_id`, `order_index`, `display_label`, and `hierarchy` in `frontend/src/workbench/UnitTree.tsx`
- [ ] T032 [US1] Implement selected unit source, evidence, validation finding, semantic draft, reference candidate, dependency edge, and extraction provenance display in `frontend/src/workbench/UnitReviewPanel.tsx`
- [ ] T033 [US1] Implement semantic draft edit tracking and reviewer notes in `frontend/src/workbench/reviewSession.ts`
- [ ] T034 [US1] Implement curation note and review decision recording in `frontend/src/workbench/ReviewArtifactPanel.tsx`
- [ ] T035 [US1] Implement export controls for `StructuringReviewPatch`, `StructuringReviewDecision`, `AssetCurationRecord`, and `IntegratedStructuringReviewPackage` in `frontend/src/workbench/ArtifactExportPanel.tsx`
- [ ] T036 [US1] Integrate the complete curation workbench route in `frontend/src/App.tsx`

**Checkpoint**: User Story 1 is independently usable as the MVP.

---

## Deferred Phase 4: Post-MVP Runtime Scenario Preview (Priority: P2)

**Goal**: Users can enter a scenario, submit it only through the mocked/future adapter boundary, and view a non-final placeholder judgment draft with citations, evidence, confidence, warnings, validation status, and review requirement.

**Independent Test**: Submit a scenario against `frontend/src/adapters/mockRuntimeAdapter.ts` and verify the rendered result is draft-only, sourced from mock data, and does not call runtime, LLM, retrieval, vector search, or rule execution.

### Tests for User Story 2

- [ ] T037 [P] [US2] Write mocked runtime adapter tests in `frontend/tests/contract/mockRuntimeAdapter.contract.test.ts`
- [ ] T038 [P] [US2] Write runtime scenario input contract tests in `frontend/tests/contract/runtimeScenarioInput.contract.test.ts`
- [ ] T039 [P] [US2] Write runtime judgment draft display tests in `frontend/tests/contract/runtimeJudgmentDraft.contract.test.ts`
- [ ] T040 [P] [US2] Write Playwright smoke test for mocked scenario submission in `frontend/tests/smoke/runtime-scenario-flow.spec.ts`

### Implementation for User Story 2

- [ ] T041 [US2] Implement placeholder runtime scenario form in `frontend/src/workbench/RuntimeScenarioInputForm.tsx`
- [ ] T042 [US2] Implement mocked adapter submission state in `frontend/src/workbench/runtimeScenarioSession.ts`
- [ ] T043 [US2] Implement non-final judgment draft display in `frontend/src/workbench/RuntimeJudgmentDraftView.tsx`
- [ ] T044 [US2] Implement runtime draft warnings, confidence, validation status, and human-review indicators in `frontend/src/workbench/RuntimeJudgmentDraftView.tsx`
- [ ] T045 [US2] Integrate the runtime scenario preview route in `frontend/src/App.tsx`

**Checkpoint**: User Story 2 works with mocked runtime data and no runtime implementation.

---

## Deferred Phase 5: Post-MVP Runtime Evidence And Trace Preview (Priority: P3)

**Goal**: Reviewers can inspect placeholder runtime citations, evidence, sanitized traces, and record review notes or decisions without promoting anything into rules, reviewed runtime assets, or final compliance conclusions.

**Independent Test**: Load `frontend/src/fixtures/runtime-draft.mock.json`, inspect citations/evidence/trace, verify incomplete citations and redactions are visible, and save a review artifact that remains curation-only.

### Tests for User Story 3

- [ ] T046 [P] [US3] Write runtime citation and incomplete-citation tests in `frontend/tests/contract/runtimeCitation.contract.test.ts`
- [ ] T047 [P] [US3] Write runtime evidence display tests in `frontend/tests/contract/runtimeEvidence.contract.test.ts`
- [ ] T048 [P] [US3] Write sanitized trace and redaction tests in `frontend/tests/contract/runtimeTrace.contract.test.ts`
- [ ] T049 [P] [US3] Write Playwright smoke test for evidence and trace inspection in `frontend/tests/smoke/runtime-evidence-trace.spec.ts`

### Implementation for User Story 3

- [ ] T050 [US3] Implement citation inspection and incomplete-citation labeling in `frontend/src/workbench/RuntimeCitationView.tsx`
- [ ] T051 [US3] Implement evidence inspection with bounded excerpts and as-of-date basis in `frontend/src/workbench/RuntimeEvidenceView.tsx`
- [ ] T052 [US3] Implement sanitized trace inspection with redaction warnings in `frontend/src/workbench/RuntimeTraceView.tsx`
- [ ] T053 [US3] Implement runtime inspection review notes and decisions as review artifacts only in `frontend/src/workbench/RuntimeReviewArtifactPanel.tsx`
- [ ] T054 [US3] Integrate evidence and trace inspection panels into the runtime draft view in `frontend/src/workbench/RuntimeJudgmentDraftView.tsx`

**Checkpoint**: User Story 3 supports evidence and trace inspection through mocked/future-adapter data only.

---

## Phase 6: Polish And Cross-Cutting Verification

**Purpose**: Confirm the full 003 frontend slice remains aligned with the spec, contracts, and exclusion boundaries.

- [ ] T055 [P] Add implementation validation notes to `frontend/README.md`; update `specs/003-arbiter-workbench-ui/quickstart.md` only for non-normative clarification
- [ ] T056 [P] Add frontend README notes for mock-only runtime behavior in `frontend/README.md`
- [ ] T057 Run the frontend contract and unit test suite defined in `frontend/package.json`
- [ ] T058 Run Playwright smoke tests defined in `frontend/playwright.config.ts`
- [ ] T059 Verify with git diff, dependency inspection, and boundary tests that no forbidden 001 schema mutation, 001 pipeline reimplementation, direct model-provider call, 002 runtime, database, retrieval, vector search, rule execution, active `RulePack`, formal `RuleItem`, final `JudgmentResult`, or PDF/DOCX parsing changes were introduced in `frontend/`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Deferred Phase 4)**: Post-MVP only; depends on Foundational and must remain mock/future-adapter UI.
- **User Story 3 (Deferred Phase 5)**: Post-MVP only; depends on runtime placeholder contracts and may reuse US2 draft display.
- **Polish (Phase 6)**: Depends on desired user stories being complete.

### User Story Dependencies

- **US1 - Curate Reviewed Regulation Data Assets**: No dependency on US2 or US3 after Foundational.
- **US2 - Preview Future Runtime Scenario Flow**: Deferred until after the Markdown-to-001 review MVP; uses mocked runtime data only.
- **US3 - Inspect Future Runtime Evidence And Trace**: Deferred until after US2; depends on runtime placeholder contracts from Foundational.

### Parallel Opportunities

- Setup tasks T003-T006 can run in parallel after T001-T002.
- Foundational tests T008-T011 can run in parallel.
- Fixture tasks T015-T017 can run in parallel.
- US1 tests T023-T027 can run in parallel before US1 implementation.
- US2 tests T037-T040 can run in parallel before US2 implementation.
- US3 tests T046-T049 can run in parallel before US3 implementation.

---

## Parallel Example: User Story 1

```bash
Task: "T023 fixture load and invalid-input tests in frontend/tests/fixtures/structuringOutputLoad.test.ts"
Task: "T024 unit tree contract tests in frontend/tests/contract/unitTree.contract.test.ts"
Task: "T025 document metadata contract tests in frontend/tests/contract/documentMetadata.contract.test.ts"
Task: "T026 review export contract tests in frontend/tests/contract/reviewExport.contract.test.ts"
```

## Parallel Example: User Story 2

```bash
Task: "T037 mocked runtime adapter tests in frontend/tests/contract/mockRuntimeAdapter.contract.test.ts"
Task: "T038 runtime scenario input contract tests in frontend/tests/contract/runtimeScenarioInput.contract.test.ts"
Task: "T039 runtime judgment draft display tests in frontend/tests/contract/runtimeJudgmentDraft.contract.test.ts"
```

## Parallel Example: User Story 3

```bash
Task: "T046 runtime citation tests in frontend/tests/contract/runtimeCitation.contract.test.ts"
Task: "T047 runtime evidence display tests in frontend/tests/contract/runtimeEvidence.contract.test.ts"
Task: "T048 sanitized trace tests in frontend/tests/contract/runtimeTrace.contract.test.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup.
2. Complete Phase 2 foundational contracts, fixtures, mock adapter, and boundary guards.
3. Complete Phase 3 User Story 1.
4. Stop and validate Markdown intake, JSON fixture load, document metadata review, unit tree review, semantic edit tracking, curation note capture, integrated package export, and base-output immutability.

### Incremental Delivery

1. Add US1 to make 001 `StructuringPipelineOutput` curation usable.
2. Defer US2 until the Markdown-to-001 review/export MVP is accepted.
3. Defer US3 until runtime preview is intentionally reopened.
4. Run final boundary checks before any handoff.

### Boundary Guardrails

- Keep all implementation under `frontend/` except for 003 documentation updates.
- Treat Markdown as the primary source for Admin adapter invocation and 001 JSON
  as replay/debug input only.
- Keep all model calls and canonical schema validation inside 001 /
  `LLMClient / ModelProvider`; frontend code only creates requests, validates
  responses, and renders review/edit/export surfaces.
- Treat 002 runtime contracts as replaceable frontend placeholders only.
- Do not create database storage, direct model calls, retrieval, vector search,
  rule execution, active rules, final judgments, or raw document parsing in 003.
