# Feature Specification: Arbiter Workbench UI

**Feature Branch**: `003-arbiter-workbench-ui`  
**Created**: 2026-05-13  
**Status**: Draft  
**Input**: User description: "Create the frontend workbench for 001 regulation structuring review and 002 agent runtime workflow inspection, UI-only."

The Arbiter Workbench UI is a frontend workbench for expert-facing review,
correction, and curation of regulation data assets. The MVP centers on
curating `StructuringPipelineOutput` JSON outputs from 001 Regulation
Structuring while also preparing runtime-facing UI surfaces for future 002
Agent Runtime integration through mocked or future adapters only. The first
implementation is data-asset curation first and runtime-adapter-ready second.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Curate Reviewed Regulation Data Assets (Priority: P1)

A compliance, legal, or business expert opens a fixture or exported
`StructuringPipelineOutput` JSON conforming to 001, reviews the document and
unit tree, compares draft units against preserved source evidence, corrects
semantic draft fields, records curation notes, and exports auditable review and
curation artifacts that help accumulate reviewed regulation data assets without
modifying the source JSON in place.

**Why this priority**: This is the first workbench value path because 001
produces draft-only assets that require expert review and curation before any
later handoff or promotion workflow can be considered.

**Independent Test**: Can be tested by loading a valid 001-compatible fixture
JSON, selecting multiple units, editing draft fields, adding curation notes, and
exporting review or curation artifacts that reference the original output.

**Acceptance Scenarios**:

1. **Given** a valid `StructuringPipelineOutput` JSON, **When** the expert opens it, **Then** the workbench displays a navigable unit tree using `parent_unit_id`, `order_index`, `display_label`, `hierarchy`, warnings, and `review_status`.
2. **Given** the document metadata panel is open, **When** the expert reviews draft document metadata, **Then** the workbench shows title, `document_number`, classification, dates, temporal metadata, warnings, validation findings, and `review_status` as reviewable fields without mutating the loaded source JSON.
3. **Given** a selected regulation unit, **When** the expert reviews it, **Then** the workbench shows original text, normalized text, source location, evidence text, validation findings, and editable semantic draft fields side by side.
4. **Given** an edited semantic draft field, **When** the expert exports the review result, **Then** the workbench saves a separate `StructuringReviewPatch` containing `source_output_ref`, `target_type`, `target_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, `reviewed_at`, and optional `unit_id`.
5. **Given** the expert records a document, unit, semantic draft, reference candidate, dependency edge, or curation-note decision, **When** the decision is exported, **Then** the workbench saves a separate `StructuringReviewDecision` linked to the same source output.
6. **Given** the source 001 JSON is loaded, **When** the expert saves review work, **Then** the original 001 output remains unchanged and all review changes are captured in separate review or curation artifacts.

---

### User Story 2 - Preview Future Runtime Scenario Flow (Priority: P2)

A compliance user enters a natural-language compliance question or structured
business scenario into a placeholder runtime scenario screen, submits it through
a mocked or future 002 adapter, and reviews the returned placeholder judgment
draft, evidence, citations, confidence, warnings, validation status, and
human-review requirement.

**Why this priority**: Runtime scenario entry and result inspection prepare the
workbench for later 002 workflows while keeping this feature UI-only and free of
runtime execution.

**Independent Test**: Can be tested with a mocked runtime response that follows the frontend placeholder contract and contains a judgment draft, citations, evidence, trace summary, confidence, and review status.

**Acceptance Scenarios**:

1. **Given** the runtime scenario module is open, **When** the user enters a natural-language question or structured scenario fields, **Then** the workbench can submit that scenario only to a mocked or future 002 adapter without calling an LLM, retrieval system, rule engine, or runtime directly.
2. **Given** a placeholder runtime judgment draft response, **When** the workbench renders the result, **Then** it clearly labels the output as a draft and not a final compliance conclusion.
3. **Given** a response includes citations, evidence, confidence, warnings, and review requirements, **When** the user inspects the result, **Then** each item is visible and associated with the judgment draft it supports.

---

### User Story 3 - Inspect Future Runtime Evidence And Trace (Priority: P3)

A reviewer opens a mocked or future-adapter runtime judgment draft, inspects
cited regulation units, source document/version, article or clause number,
provided provenance, sanitized trace summaries, warnings, review-status gates,
and records review notes or review decision artifacts.

**Why this priority**: Reviewer inspection prepares traceable runtime-facing UI
surfaces while preventing this feature from implementing 002 runtime behavior or
promoting drafts into final compliance conclusions.

**Independent Test**: Can be tested by loading a mocked runtime draft with multiple citations and trace steps, then recording review notes while verifying no secrets, full prompts, or provider payloads are displayed.

**Acceptance Scenarios**:

1. **Given** a runtime draft contains cited regulation context, **When** the reviewer opens the evidence viewer, **Then** the workbench displays stable regulation unit IDs, source document/version, article or clause numbers where available, adapter-provided provenance, and as-of-date basis.
2. **Given** a runtime draft contains trace steps, **When** the reviewer opens the trace viewer, **Then** the workbench displays sanitized trace summaries and hides secrets, full prompts, provider payloads, and unnecessary sensitive raw text.
3. **Given** a reviewer records notes or a decision, **When** the artifact is saved, **Then** it remains a review artifact and does not produce active rules, reviewed runtime assets, or final compliance decisions.

### Edge Cases

- Invalid or schema-incompatible `StructuringPipelineOutput` JSON must be rejected with readable validation feedback and must not be silently edited.
- Missing `parent_unit_id`, `order_index`, `display_label`, hierarchy, source location, evidence text, or review status must be shown as incomplete data rather than fabricated.
- Units with `draft`, `needs_review`, `approved`, `rejected`, or `superseded` states must be visually distinguishable where those states appear.
- A runtime response with missing stable citation identifiers must be flagged as incomplete; free-text citation labels alone are insufficient.
- Runtime traces containing secrets, full prompts, provider payloads, or unnecessary sensitive raw text must be redacted or blocked from display.
- Attempts to upload PDF or Word files directly into this feature must be rejected or routed outside scope; this feature accepts 001 JSON for structuring review, not raw document parsing.
- Unsaved review edits must be distinguishable from exported review artifacts so reviewers do not mistake local edits for an auditable record.
- Multiple unsaved edits to the same target and `field_path` must not silently overwrite audit context; the workbench must make clear whether export produces a patch sequence or the latest consolidated patch.
- Runtime-facing screens must remain usable with mocked responses when 002 Agent Runtime does not exist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The workbench MUST provide a regulation data-asset curation module that accepts fixture or exported JSON conforming to 001 `StructuringPipelineOutput` as the input contract.
- **FR-002**: The workbench MUST validate loaded 001 JSON against the expected review input shape and display validation failures instead of opening invalid data as editable review content.
- **FR-003**: The workbench MUST display the document/unit tree using `parent_unit_id`, `order_index`, `display_label`, `hierarchy`, warnings, and `review_status` when available.
- **FR-004**: The workbench MUST display original text, normalized text, source location, evidence text, and validation findings for the selected regulation unit.
- **FR-005**: The workbench MUST allow experts to edit semantic draft fields and add reviewer notes without mutating the loaded 001 source JSON in place.
- **FR-006**: The MVP MUST be usable with fixture JSON conforming to `StructuringPipelineOutput` without requiring 001 pipeline execution or 002 runtime availability.
- **FR-007**: The workbench MUST export a separate `StructuringReviewPatch` for each reviewed edit using `source_output_ref`, `target_type`, `target_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, `reviewed_at`, and optional `unit_id`.
- **FR-008**: The workbench MUST export a separate `StructuringReviewDecision` when a reviewer records a decision for a document-level target, unit-level target, semantic draft, reference candidate, dependency edge, or curation note.
- **FR-009**: Review and curation artifacts MUST use `source_output_ref` with `contract_version`, `document_id`, `source_id`, `source_file`, and `loaded_at`; hashes are not required.
- **FR-010**: Review artifacts MUST preserve audit history by referencing the source 001 output and by avoiding unnecessary duplication of full original regulation text.
- **FR-011**: The workbench SHOULD support an `AssetCurationRecord` for expert notes, candidate rule hints, scenario examples, ambiguity cases, and dependency issues.
- **FR-012**: `StructuringReviewPatch`, `StructuringReviewDecision`, and `AssetCurationRecord` MUST remain review or curation artifacts only and MUST NOT become active `RulePack`, formal `RuleItem`, runtime-safe reviewed assets, final `JudgmentResult`, or final compliance decisions.
- **FR-013**: The workbench MUST clearly distinguish draft, `needs_review`, `approved`, `rejected`, and `superseded` states where those statuses appear in loaded or review artifacts.
- **FR-014**: The workbench MUST make clear that draft structuring outputs and runtime outputs are not final compliance decisions.
- **FR-015**: The workbench MUST provide a placeholder `RuntimeScenarioInput` form that accepts a natural-language compliance question and optional structured business scenario fields.
- **FR-016**: The runtime scenario flow MUST submit scenarios only through a mocked or future 002 adapter and MUST NOT call LLMs, retrieval systems, vector search, rule execution, or 002 runtime logic directly.
- **FR-017**: The workbench MUST define placeholder frontend-facing UI contracts for `RuntimeScenarioInput`, `RuntimeJudgmentDraftView`, `RuntimeCitationView`, `RuntimeEvidenceView`, and `RuntimeTraceView` until 002 finalizes its schemas.
- **FR-018**: Placeholder runtime UI contracts MUST be explicitly marked as UI contracts and MUST NOT be treated as final 002 runtime schemas.
- **FR-019**: Placeholder runtime UI contracts MUST remain replaceable once 002 finalizes its runtime schemas and MUST NOT be treated as backend or domain-level 002 schemas.
- **FR-020**: `RuntimeJudgmentDraftView` MUST display draft judgment content, confidence, warnings, validation status, human-review requirement, citations, evidence, and trace summary when provided by a mocked or future adapter.
- **FR-021**: `RuntimeCitationView` MUST display stable regulation unit IDs, source document/version, article or clause number where available, provided provenance, and as-of-date basis; free-text labels alone MUST be flagged as insufficient.
- **FR-022**: `RuntimeEvidenceView` MUST display provided regulation units, dependency context, citation provenance, and as-of-date basis when supplied by a mocked or future adapter.
- **FR-023**: `RuntimeTraceView` MUST display sanitized trace steps and MUST NOT expose secrets, full prompts, provider payloads, or unnecessary sensitive raw text.
- **FR-024**: The feature MUST NOT implement the 001 structuring pipeline, 002 Agent Runtime, retrieval, vector search, rule execution, LLM calls, production asset promotion, or final compliance decision logic.
- **FR-025**: The feature MUST NOT generate active `RulePack`, formal `RuleItem`, final `JudgmentResult`, runtime-safe reviewed assets, or final compliance conclusions.
- **FR-026**: The feature MUST NOT parse PDF or Word files and MUST NOT treat raw policy or regulation documents as direct structuring inputs.

### Constitution Alignment *(mandatory for Arbiter features)*

- **CA-001**: Feature scope is a frontend workbench across Admin review and future Agent Runtime inspection; it does not implement Admin parsing, Agent Runtime execution, shared asset promotion, or compliance decision logic.
- **CA-002**: Runtime-facing behavior in this feature is limited to scenario submission and draft response display; the workbench MUST NOT parse raw regulation files for runtime use or present draft assets as runtime-safe reviewed assets.
- **CA-003**: This feature MUST NOT make direct LLM calls. It may display LLM-derived draft fields from 001 outputs, but those fields remain draft/review material until handled by a separate review or promotion workflow.
- **CA-004**: Regulation review views and runtime draft views MUST preserve source version, effective date, expiration date, amendment/source-version relation, and as-of-date basis where available.
- **CA-005**: Judgment draft views MUST cite stable regulation unit IDs, source document/version, article or clause number where available, and adapter-provided provenance when supplied; free-text citation labels are insufficient.
- **CA-006**: Workbench inputs, exported review artifacts, and placeholder runtime view contracts MUST be represented as explicit JSON-compatible contracts rather than hidden prompt conventions.
- **CA-007**: Sensitive data, secrets, logs, traces, and human review status MUST have explicit display and export handling requirements; sanitized traces are required for runtime review.
- **CA-008**: User-facing compliance outputs MUST remain judgment drafts for human review and MUST NOT claim to replace final compliance decisions.

### Key Entities *(include if feature involves data)*

- **StructuringPipelineOutput**: Existing 001 draft output used as the review module input. It provides document metadata, draft regulation units, semantic draft fields, evidence, validation findings, provenance, and review status.
- **SourceOutputRef**: Stable source reference used by review and curation artifacts. Key attributes include `contract_version`, `document_id`, `source_id`, `source_file`, and `loaded_at`; hashes are not required.
- **StructuringReviewPatch**: Separate auditable artifact for reviewed edits against generic targets. Key attributes include `source_output_ref`, `target_type`, `target_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, `reviewed_at`, optional `unit_id` for unit-level edits, and optional `reviewer_identity` when available. Identity management remains outside this feature.
- **StructuringReviewDecision**: Separate auditable artifact for reviewer decisions targeting a document-level item, unit-level item, semantic draft, reference candidate, dependency edge, or curation note. It records the reviewed target, decision status, reviewer notes, timestamp, optional `reviewer_identity` when available, and source output reference without promoting assets. Identity management remains outside this feature.
- **AssetCurationRecord**: Optional curation artifact for expert notes, candidate rule hints, scenario examples, ambiguity cases, and dependency issues. It may include optional `reviewer_identity` when available, but identity management remains outside this feature. It remains review material and is not an active `RulePack`, formal `RuleItem`, runtime-safe reviewed asset, or final compliance decision.
- **RuntimeScenarioInput**: Placeholder UI contract for a natural-language compliance question and optional structured business scenario fields. It remains frontend-facing until 002 finalizes its runtime input contract.
- **RuntimeJudgmentDraftView**: Placeholder UI contract for displaying a future runtime judgment draft, confidence, warnings, validation status, review requirement, citations, evidence, and trace summary. It is not a final `JudgmentResult`.
- **RuntimeCitationView**: Placeholder UI contract for stable regulation unit ID, source document/version, article or clause number where available, adapter-provided provenance, and as-of-date basis.
- **RuntimeEvidenceView**: Placeholder UI contract for cited or provided regulation evidence, dependency context, citation provenance, and as-of-date basis.
- **RuntimeTraceView**: Placeholder UI contract for sanitized trace steps suitable for reviewer inspection without secrets, full prompts, provider payloads, or unnecessary sensitive raw text.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An expert can load a valid sample 001 `StructuringPipelineOutput` fixture without running 001 or 002, browse the unit tree, inspect one unit's source/evidence/semantic fields, edit a semantic field, add a curation note, and export review or curation artifacts in one review session.
- **SC-002**: For a sample with at least 10 regulation units, the displayed tree preserves parent-child relationships and ordering from `parent_unit_id` and `order_index` with no review-visible ordering mismatches.
- **SC-003**: Exported review patches contain every required audit field (`source_output_ref`, `target_type`, `target_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, `reviewed_at`, and optional `unit_id`) and do not duplicate full original regulation text unnecessarily.
- **SC-004**: A user can submit a runtime scenario through the workbench to a mocked or future 002 adapter and view a runtime judgment draft with citations, evidence, confidence, warnings, validation status, and review-status indicators when the response provides them.
- **SC-005**: All displayed runtime citations with available metadata show stable regulation unit ID, source document/version, article or clause number where available, adapter-provided provenance, and as-of-date basis; incomplete citations are visibly flagged.
- **SC-006**: Runtime trace display validation confirms that secrets, full prompts, provider payloads, and unnecessary sensitive raw text are not shown to reviewers.
- **SC-007**: Across structuring review and runtime scenario flows, draft outputs are labeled as non-final, and the feature produces no LLM calls, runtime logic, retrieval logic, rule execution, active `RulePack`, formal `RuleItem`, final `JudgmentResult`, or final compliance conclusion.
- **SC-008**: Invalid or schema-incompatible `StructuringPipelineOutput` input is rejected with readable validation feedback and no editable review session is created.

## Assumptions

- The review module consumes 001 `StructuringPipelineOutput` JSON as an existing contract; this feature does not define or run the 001 structuring pipeline.
- The final 002 Agent Runtime contract is not assumed to exist yet; runtime contracts in this feature are frontend-facing placeholders for UI development and mock validation.
- Fixture JSON conforming to `StructuringPipelineOutput` is sufficient for MVP validation; live 001 pipeline execution and 002 runtime availability are not required.
- Reviewer identity is recorded only when available; identity management is outside this feature.
- The first workbench scope is a desktop-oriented expert review and inspection experience; mobile optimization is not a primary success criterion for this feature.
- Sample 001 outputs and mocked runtime responses may be used for validation, but they must not be promoted to production runtime assets by this feature.
