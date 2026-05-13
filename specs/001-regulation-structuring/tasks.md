# Tasks: Regulation Structuring Pipeline

**Input**: Design documents from `/specs/001-regulation-structuring/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are required. Write failing tests before implementation where practical.

**Organization**: Tasks are grouped by user story so each story can be implemented and verified independently.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because the task touches different files or has no dependency on another pending task
- **[Story]**: User story label, for example [US1], [US2], [US3], [US4]
- Include exact file paths in each task description

## Phase 1: Setup

**Purpose**: Establish the Admin-only structuring package and test fixture layout.

- [X] T001 Create structuring package and fixture directories: `src/arbiter/structuring/`, `src/arbiter/schemas/`, and `tests/structuring/fixtures/`
- [X] T002 Create package init files and schema export placeholder in `src/arbiter/structuring/__init__.py` and `src/arbiter/schemas/__init__.py`
- [X] T003 Add concise Markdown/text fixture documents and edge-case fixture files under `tests/structuring/fixtures/`

## Phase 2: Foundational Schemas and Test Fixtures

**Purpose**: Define contracts that every story depends on before pipeline behavior is implemented.

- [X] T004 [P] Write failing Pydantic schema tests for all regulation structuring enums, models, required fields, forbidden extras, and `review_status` defaults in `tests/structuring/test_regulation_structuring_schemas.py`
- [X] T005 [P] Write failing JSON round-trip and sanitization tests for `StructuringPipelineOutput` serialization, parsing, and rejection of secrets, full prompts, provider payloads, absolute local paths, or unnecessary raw sensitive text in `tests/structuring/test_regulation_structuring_roundtrip.py`
- [X] T006 Inspect the existing `LLMClient` / `ModelProvider` abstraction in `src/arbiter/` and record the real import path and expected method signature in tests/structuring/conftest.py comments or a small test-local note before implementing `tests/structuring/conftest.py`; do not invent a new model access layer
- [X] T007 [P] Write failing mock `ModelProvider` fixture tests proving LLM-assisted extraction behavior uses mocks and never real model calls in `tests/structuring/test_llm_structuring_validation.py`
- [X] T008 Implement Pydantic enums and shared primitive models, including `ReviewStatus`, identifier fields, source location primitives, confidence fields, and evidence/ambiguity primitives, in `src/arbiter/schemas/regulation_structuring.py`. Do not introduce extra primitive wrapper models unless already required by the data model; simple typed fields are acceptable.
- [X] T009 Implement document, classification, temporal, and provenance models, including `RegulationDocumentDraft`, `DocumentClassificationDraft`, `TemporalMetadata`, and `ExtractionProvenance`, in `src/arbiter/schemas/regulation_structuring.py`
- [X] T010 Implement unit and semantic unit models, including `RegulationUnitDraft`, `HierarchyPath`, `parent_unit_id`, `order_index`, `display_label`, and expanded `SemanticUnitDraft` fields, in `src/arbiter/schemas/regulation_structuring.py`
- [X] T011 Implement reference and dependency graph models, including `ReferenceCandidate`, `DependencyEdgeDraft`, `RegulationUnitRelationDraft` as a compatibility alias for the same draft edge schema, unresolved external title clues, and draft graph records, in `src/arbiter/schemas/regulation_structuring.py`
- [X] T012 Implement validation report and output bundle models, including `StructuringValidationFinding`, `StructuringValidationReport`, and not-runtime-safe `StructuringPipelineOutput`, in `src/arbiter/schemas/regulation_structuring.py`
- [X] T013 Export regulation structuring schemas from `src/arbiter/schemas/__init__.py`
- [X] T014 Implement JSON export and parse helpers with sanitization guards for secrets, full prompts, provider payloads, absolute local paths, and unnecessary raw sensitive text in `src/arbiter/structuring/export.py`
- [X] T015 Implement reusable mock `ModelProvider` fixtures and blocked-real-call guards in `tests/structuring/conftest.py`
- [X] T016 Run foundational checks with `PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring/test_regulation_structuring_schemas.py tests/structuring/test_regulation_structuring_roundtrip.py tests/structuring/test_llm_structuring_validation.py -q`

## Phase 3: User Story 1 - Generate Structured Draft (P1)

**Goal**: An admin can submit Markdown or normalized regulation text and receive a draft-only structured bundle with validation data. PDF/Word are not direct structuring inputs.

**Independent Test**: Submit a fixture regulation with recognizable hierarchy and verify `RegulationDocumentDraft`, `RegulationUnitDraft[]`, `StructuringValidationReport`, and no judgment or formal rule output.

- [ ] T017 [P] [US1] Write failing intake tests for direct Markdown and normalized text inputs plus the optional `FileInput -> ExtractedTextBundle -> NormalizedTextInput` boundary in `tests/structuring/test_intake.py`
- [ ] T018 [P] [US1] Write failing structure-first splitting tests for Markdown headings, `第X条` / `Article X`, numbered paragraphs or list items, paragraph fallback, and token-count fallback warnings in `tests/structuring/test_structure_first_splitting.py`
- [ ] T019 [P] [US1] Write failing pipeline happy-path tests for draft document output, draft unit list, validation report, and forbidden-output exclusion in `tests/structuring/test_regulation_structuring_pipeline.py`
- [ ] T020 [P] [US1] Write failing mock LLM schema-validation tests proving LLM boundary proposals only supplement deterministic candidates, accepted proposals pass Pydantic validation, ambiguous proposals create validation findings, and invalid model output is rejected in `tests/structuring/test_llm_structuring_validation.py`
- [ ] T021 [US1] Implement Markdown and normalized text intake plus the optional file-intake adapter boundary without OCR, password handling, or full layout recovery in `src/arbiter/structuring/intake.py`
- [ ] T022 [US1] Implement structure-first deterministic candidate splitting by Markdown headings, `第X条` / `Article X`, numbered paragraphs or list items, and paragraph fallback; allow token-count splitting only as a last-resort warning in `src/arbiter/structuring/extraction.py`
- [ ] T023 [US1] Implement LLM-assisted extraction wrapper through existing `LLMClient` / `ModelProvider` so LLM proposals only supplement deterministic candidates and Pydantic failures become validation findings in `src/arbiter/structuring/llm_extraction.py`
- [ ] T024 [US1] Implement `RegulationStructuringPipeline` orchestration that emits only draft assets plus validation data in `src/arbiter/structuring/pipeline.py`
- [ ] T025 [US1] Verify US1 with `PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring/test_intake.py tests/structuring/test_structure_first_splitting.py tests/structuring/test_regulation_structuring_pipeline.py tests/structuring/test_llm_structuring_validation.py -q`

## Phase 4: User Story 2 - Inspect Traceable Units (P2)

**Goal**: Each structured unit preserves source traceability, explicit tree navigation metadata, and temporal/version uncertainty for later review UI and runtime context assembly.

**Independent Test**: Inspect generated draft units and verify source text, hierarchy labels, parent/order/display metadata, temporal metadata, and ambiguity findings.

- [ ] T026 [P] [US2] Write failing tests for `SourceLocation`, `original_text`, stable `source_id` / `document_id` linkage, and hierarchy label preservation in `tests/structuring/test_traceable_units.py`
- [ ] T027 [P] [US2] Write failing tests for `parent_unit_id`, `order_index`, and `display_label` tree rendering invariants in `tests/structuring/test_unit_tree.py`
- [ ] T028 [P] [US2] Write failing tests for `TemporalMetadata` fields, null/unknown handling, amendment notes, validity notes, and temporal ambiguity findings in `tests/structuring/test_temporal_metadata.py`
- [ ] T029 [US2] Implement source location, original text preservation, hierarchy path labels, and stable `source_id` / `document_id` linkage in `src/arbiter/structuring/extraction.py`
- [ ] T030 [US2] Implement explicit unit tree assignment for `parent_unit_id`, `order_index`, and `display_label` in `src/arbiter/structuring/extraction.py`
- [ ] T031 [US2] Implement temporal/version validation findings for missing, uncertain, or conflicting temporal metadata in `src/arbiter/structuring/validation.py`
- [ ] T032 [US2] Verify US2 with `PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring/test_traceable_units.py tests/structuring/test_unit_tree.py tests/structuring/test_temporal_metadata.py -q`

## Phase 5: User Story 3 - Review Warnings and Draft Semantics (P3)

**Goal**: The pipeline reports structuring concerns and keeps semantic extraction, reference candidates, and dependency drafts reviewable and separated.

**Independent Test**: Process ambiguous fixtures and verify validation findings, separated reference candidates, draft dependency edges, and evidence-backed semantic draft fields.

- [ ] T033 [P] [US3] Write failing validation report tests for duplicate article numbers, malformed hierarchy, invalid tree links, missing provenance, conflicting dates, schema failures, ambiguous boundaries, and unclear references in `tests/structuring/test_structuring_validation_report.py`
- [ ] T034 [P] [US3] Write failing tests proving `ReferenceCandidate` and `DependencyEdgeDraft` / `RegulationUnitRelationDraft` remain separate draft/unresolved structures, cross-document links stay ambiguous unless clearly supported by provided text, external document title clues do not trigger database or asset-registry lookup, and no `ReviewedDependencyEdge` is produced in `tests/structuring/test_reference_dependency_graph.py`
- [ ] T035 [P] [US3] Write failing expanded `SemanticUnitDraft` tests for `trigger_events`, `required_actions`, `prohibited_actions`, `deadlines`, `thresholds`, `subject_scope`, `object_scope`, and `reporting_obligations` with evidence and `needs_review` status in `tests/structuring/test_semantic_unit_draft.py`
- [ ] T036 [US3] Implement `StructuringValidationReport` assembly and validation finding codes in `src/arbiter/structuring/validation.py`
- [ ] T037 [US3] Implement internal reference detection, external document title clue capture, and separate `DependencyEdgeDraft` / `RegulationUnitRelationDraft` graph assembly while keeping cross-document links draft/unresolved unless clearly supported by provided text, without database lookup, local asset-registry lookup, final reviewed links, or `ReviewedDependencyEdge` output in `src/arbiter/structuring/extraction.py`
- [ ] T038 [US3] Implement expanded `SemanticUnitDraft` mapping from validated mock LLM outputs while keeping all semantic fields draft-only in `src/arbiter/structuring/llm_extraction.py`
- [ ] T039 [US3] Verify US3 with `PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring/test_structuring_validation_report.py tests/structuring/test_reference_dependency_graph.py tests/structuring/test_semantic_unit_draft.py -q`

## Phase 6: User Story 4 - Preserve Runtime Boundary (P4)

**Goal**: The feature remains Admin-only and produces no runtime-safe assets, runtime agent behavior, or final compliance conclusions.

**Independent Test**: Verify the pipeline output is not runtime-safe and no runtime agent/tool integration or formal rule/judgment artifacts are introduced.

- [ ] T040 [P] [US4] Write failing runtime boundary negative tests that pass without creating `src/arbiter/agent/`, `src/arbiter/tools/`, `src/arbiter/runtime/`, or `src/arbiter/web/` when those paths do not exist, and verify no structuring import or registration only when those paths already exist, in `tests/structuring/test_structuring_runtime_boundary.py`
- [ ] T041 [P] [US4] Write failing forbidden-output tests for `JudgmentResult`, active `RulePack`, formal `RuleItem`, final compliance conclusion fields, and runtime-safe reviewed assets in `tests/structuring/test_structuring_runtime_boundary.py`
- [ ] T042 [P] [US4] Write failing review-status boundary tests proving the pipeline creates only `needs_review` outputs and never assigns `approved`, `rejected`, or `superseded` in `tests/structuring/test_review_status_boundaries.py`
- [ ] T043 [US4] Keep structuring package exports Admin-only and avoid runtime or tool registrations in `src/arbiter/structuring/__init__.py`
- [ ] T044 [US4] Implement forbidden-output assertions for `StructuringPipelineOutput` and mark it not runtime-safe in `src/arbiter/structuring/pipeline.py`
- [ ] T045 [US4] Implement `review_status = needs_review` creation enforcement while reserving other enum values for later workflows in `src/arbiter/schemas/regulation_structuring.py`
- [ ] T046 [US4] Verify US4 with `PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring/test_structuring_runtime_boundary.py tests/structuring/test_review_status_boundaries.py -q`

## Phase 7: Polish and Cross-Cutting Verification

**Purpose**: Confirm documentation and full feature slice remain aligned.

- [ ] T047 [P] Update quickstart command and artifact path notes for the implemented Admin-only structuring slice in `specs/001-regulation-structuring/quickstart.md`
- [ ] T048 Run the full structuring test slice with `PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring -q`
- [ ] T049 Check contract examples and JSON blocks remain aligned with implemented schema names in `specs/001-regulation-structuring/contracts/structuring-pipeline-contract.md`
- [ ] T050 Verify no forbidden runtime artifacts, ComplianceJudgmentAgent exposure, real model calls in tests, database or local asset-registry lookup, reviewed dependency edges, final compliance conclusions, secrets, full prompts, provider payloads, absolute local paths, or unnecessary raw sensitive text are introduced by scanning `src/arbiter/` and `tests/structuring/`

## Dependencies

- Phase 1 must complete before Phase 2.
- Phase 2 foundational schemas, mock provider fixtures, and export helpers must complete before full pipeline implementation.
- User stories can then proceed in priority order: US1 -> US2 -> US3 -> US4.
- US4 can add negative boundary tests as soon as package paths exist, but final verification depends on US1 output shape.
- Phase 7 runs after all selected user stories are complete.

## Parallel Examples

```bash
# Phase 2 independent tests
Task: "T004 schema tests in tests/structuring/test_regulation_structuring_schemas.py"
Task: "T005 round-trip tests in tests/structuring/test_regulation_structuring_roundtrip.py"
Task: "T007 mock provider tests in tests/structuring/test_llm_structuring_validation.py"

# US2 independent tests
Task: "T026 traceability tests in tests/structuring/test_traceable_units.py"
Task: "T027 tree metadata tests in tests/structuring/test_unit_tree.py"
Task: "T028 temporal metadata tests in tests/structuring/test_temporal_metadata.py"

# US4 independent negative tests
Task: "T040 runtime boundary tests in tests/structuring/test_structuring_runtime_boundary.py"
Task: "T042 review-status boundary tests in tests/structuring/test_review_status_boundaries.py"
```

## Implementation Strategy

### First Implementation Pass: Foundations Only

1. Complete Phase 1 and Phase 2.
2. Stop after package skeleton, fixtures, Pydantic schemas, schema tests, JSON round-trip tests, mock `ModelProvider` guardrails, and export helpers pass.
3. Do not implement the full pipeline until foundational schemas and tests pass.

### MVP After Foundations: US1 Only

1. Complete Phase 3.
2. Verify `StructuringPipelineOutput` contains draft document, draft units, validation report, extraction provenance, and no runtime-safe or judgment artifacts.

### Incremental Delivery

1. Add US2 to strengthen traceability, tree navigation, and temporal/version metadata.
2. Add US3 to strengthen validation findings, semantic draft fields, references, and dependency drafts.
3. Add US4 to lock the Admin/Runtime boundary with negative tests.

### Boundary Guardrails

- Keep this feature Admin-only.
- Do not implement frontend UI.
- Do not implement `ComplianceJudgmentAgent` integration.
- Do not implement production review or promotion workflow.
- Do not implement `JudgmentResult`, active `RulePack`, formal `RuleItem`, or final compliance conclusions.
- Do not make real model calls in tests; use mock `ModelProvider` fixtures only.
- Do not query a database or local asset registry, create final reviewed links, or produce `ReviewedDependencyEdge`.
- Keep `StructuringPipelineOutput` explicitly not runtime-safe.
