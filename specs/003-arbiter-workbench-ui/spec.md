# Feature Specification: Arbiter Workbench UI

**Feature Branch**: `003-arbiter-workbench-ui`  
**Created**: 2026-05-13  
**Status**: Draft  
**Input**: User description: "Create the frontend workbench for 001 regulation structuring review and 002 agent runtime workflow inspection, UI-only."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Review Structured Regulation Draft (Priority: P1)

A compliance, legal, or business expert opens a `StructuringPipelineOutput` JSON produced by 001 regulation structuring, reviews the document and unit tree, compares each draft unit against preserved source evidence, corrects semantic draft fields, adds reviewer notes, and exports an auditable review artifact without modifying the source JSON in place.

**Why this priority**: This is the first workbench value path because 001 produces draft-only assets that require expert review before any later handoff.

**Independent Test**: Can be tested by loading a valid 001 output sample, selecting multiple units, editing draft fields, and exporting a review patch or review decision artifact that references the original output.

**Acceptance Scenarios**:

1. **Given** a valid `StructuringPipelineOutput` JSON, **When** the expert opens it, **Then** the workbench displays a navigable unit tree using `parent_unit_id`, `order_index`, `display_label`, `hierarchy`, warnings, and `review_status`.
2. **Given** a selected regulation unit, **When** the expert reviews it, **Then** the workbench shows original text, normalized text, source location, evidence text, validation findings, and editable semantic draft fields side by side.
3. **Given** an edited semantic draft field, **When** the expert exports the review result, **Then** the workbench saves a separate `StructuringReviewPatch` or `StructuringReviewDecision` containing `unit_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, and `reviewed_at`.
4. **Given** the source 001 JSON is loaded, **When** the expert saves review work, **Then** the original 001 output remains unchanged and all review changes are captured in a separate artifact.

---

### User Story 2 - Run Runtime Scenario From Workbench (Priority: P2)

A compliance user enters a natural-language compliance question or structured business scenario, submits it through the workbench to a future 002 runtime response source or mocked adapter, and reviews the returned runtime judgment draft, evidence, citations, confidence, warnings, validation status, and human-review requirement.

**Why this priority**: Runtime scenario entry and result inspection are the main bridge from reviewed regulation assets to later agent runtime workflows, while this feature remains UI-only.

**Independent Test**: Can be tested with a mocked runtime response that follows the frontend placeholder contract and contains a judgment draft, citations, evidence, trace summary, confidence, and review status.

**Acceptance Scenarios**:

1. **Given** the runtime scenario module is open, **When** the user enters a natural-language question or structured scenario fields, **Then** the workbench can submit that scenario to a mocked or future 002 adapter without calling an LLM directly.
2. **Given** a runtime judgment draft response, **When** the workbench renders the result, **Then** it clearly labels the output as a draft unless it is explicitly marked as reviewed by the response contract.
3. **Given** a response includes citations, evidence, confidence, warnings, and review requirements, **When** the user inspects the result, **Then** each item is visible and associated with the judgment draft it supports.

---

### User Story 3 - Inspect Runtime Evidence And Trace (Priority: P3)

A reviewer opens a runtime judgment draft, inspects cited regulation units, source document/version, article or clause number, retrieval provenance, reasoning trace, warnings, review-status gates, and records review notes or a review decision artifact.

**Why this priority**: Reviewer inspection ensures runtime drafts remain traceable and auditable without promoting them to final compliance conclusions inside this feature.

**Independent Test**: Can be tested by loading a mocked runtime draft with multiple citations and trace steps, then recording review notes while verifying no secrets, full prompts, or provider payloads are displayed.

**Acceptance Scenarios**:

1. **Given** a runtime draft contains cited regulation context, **When** the reviewer opens the evidence viewer, **Then** the workbench displays stable regulation unit IDs, source document/version, article or clause numbers where available, retrieval provenance, and as-of-date basis.
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

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The workbench MUST provide a regulation structuring review module that accepts `StructuringPipelineOutput` JSON from 001 as the input contract.
- **FR-002**: The workbench MUST validate loaded 001 JSON against the expected review input shape and display validation failures instead of opening invalid data as editable review content.
- **FR-003**: The workbench MUST display the document/unit tree using `parent_unit_id`, `order_index`, `display_label`, `hierarchy`, warnings, and `review_status` when available.
- **FR-004**: The workbench MUST display original text, normalized text, source location, evidence text, and validation findings for the selected regulation unit.
- **FR-005**: The workbench MUST allow experts to edit semantic draft fields and add reviewer notes without mutating the loaded 001 source JSON in place.
- **FR-006**: The workbench MUST export a separate `StructuringReviewPatch` containing `unit_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, and `reviewed_at` for each edited field.
- **FR-007**: The workbench MUST export a separate `StructuringReviewDecision` when a reviewer records a unit-level or document-level review decision.
- **FR-008**: Review artifacts MUST preserve audit history by referencing the source 001 output and by avoiding unnecessary duplication of full original regulation text.
- **FR-009**: The workbench MUST clearly distinguish draft, `needs_review`, `approved`, `rejected`, and `superseded` states where those statuses appear in loaded or review artifacts.
- **FR-010**: The workbench MUST make clear that draft structuring outputs and runtime outputs are not final compliance decisions.
- **FR-011**: The workbench MUST provide a runtime scenario module that accepts a natural-language compliance question and optional structured business scenario fields.
- **FR-012**: The runtime scenario module MUST submit scenarios only through a future 002 runtime contract or mocked adapter and MUST NOT call LLMs directly.
- **FR-013**: The workbench MUST define placeholder frontend-facing UI contracts for `RuntimeScenarioInput`, `RuntimeJudgmentDraftView`, `RuntimeCitationView`, and `RuntimeTraceView` until 002 finalizes its runtime contract.
- **FR-014**: Placeholder runtime UI contracts MUST be explicitly marked as UI contracts and MUST NOT be treated as final 002 runtime schemas.
- **FR-015**: The runtime result viewer MUST display draft judgment content, cited regulation units, source document/version, article or clause number where available, retrieval provenance, confidence, warnings, validation status, and human-review requirement when provided.
- **FR-016**: Runtime citations MUST include stable regulation unit IDs, source document/version, article or clause number where available, and retrieval provenance; free-text labels alone MUST be flagged as insufficient.
- **FR-017**: The evidence viewer MUST display retrieved regulation units, dependency context, citation provenance, and as-of-date basis when provided by the runtime response.
- **FR-018**: The trace viewer MUST display sanitized trace steps and MUST NOT expose secrets, full prompts, provider payloads, or unnecessary sensitive raw text.
- **FR-019**: The feature MUST NOT implement the 001 structuring pipeline, 002 Agent Runtime, retrieval, vector search, rule execution, LLM calls, production asset promotion, or final compliance decision logic.
- **FR-020**: The feature MUST NOT generate active `RulePack`, formal `RuleItem`, final `JudgmentResult`, runtime-safe reviewed assets, or final compliance conclusions.
- **FR-021**: The feature MUST NOT parse PDF or Word files and MUST NOT treat raw policy or regulation documents as direct structuring inputs.
- **FR-022**: Review notes and review decisions MUST be saved as review artifacts only and MUST NOT promote draft assets into runtime-safe assets.

### Constitution Alignment *(mandatory for Arbiter features)*

- **CA-001**: Feature scope is a frontend workbench across Admin review and future Agent Runtime inspection; it does not implement Admin parsing, Agent Runtime execution, shared asset promotion, or compliance decision logic.
- **CA-002**: Runtime-facing behavior in this feature is limited to scenario submission and draft response display; the workbench MUST NOT parse raw regulation files for runtime use or present draft assets as runtime-safe reviewed assets.
- **CA-003**: This feature MUST NOT make direct LLM calls. It may display LLM-derived draft fields from 001 outputs, but those fields remain draft/review material until handled by a separate review or promotion workflow.
- **CA-004**: Regulation review views and runtime draft views MUST preserve source version, effective date, expiration date, amendment/source-version relation, and as-of-date basis where available.
- **CA-005**: Judgment draft views MUST cite stable regulation unit IDs, source document/version, article or clause number where available, and retrieval provenance; free-text citation labels are insufficient.
- **CA-006**: Workbench inputs, exported review artifacts, and placeholder runtime view contracts MUST be represented as explicit JSON-compatible contracts rather than hidden prompt conventions.
- **CA-007**: Sensitive data, secrets, logs, traces, and human review status MUST have explicit display and export handling requirements; sanitized traces are required for runtime review.
- **CA-008**: User-facing compliance outputs MUST remain judgment drafts for human review and MUST NOT claim to replace final compliance decisions.

### Key Entities *(include if feature involves data)*

- **StructuringPipelineOutput**: Existing 001 draft output used as the review module input. It provides document metadata, draft regulation units, semantic draft fields, evidence, validation findings, provenance, and review status.
- **StructuringReviewPatch**: Separate auditable artifact for field-level reviewer edits. Key attributes include source output reference, `unit_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, and `reviewed_at`.
- **StructuringReviewDecision**: Separate auditable artifact for unit-level or document-level reviewer decisions. It records the reviewed target, decision status, reviewer notes, timestamp, and source output reference without promoting assets.
- **RuntimeScenarioInput**: Placeholder UI contract for a natural-language compliance question and optional structured business scenario fields. It remains frontend-facing until 002 finalizes its runtime input contract.
- **RuntimeJudgmentDraftView**: Placeholder UI contract for displaying a future runtime judgment draft, confidence, warnings, validation status, review requirement, citations, evidence, and trace summary. It is not a final `JudgmentResult`.
- **RuntimeCitationView**: Placeholder UI contract for stable regulation unit ID, source document/version, article or clause number where available, retrieval provenance, and as-of-date basis.
- **RuntimeTraceView**: Placeholder UI contract for sanitized trace steps suitable for reviewer inspection without secrets, full prompts, provider payloads, or unnecessary sensitive raw text.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An expert can load a valid sample 001 `StructuringPipelineOutput`, browse the unit tree, inspect one unit's source/evidence/semantic fields, edit a semantic field, and export a review patch in one review session.
- **SC-002**: For a sample with at least 10 regulation units, the displayed tree preserves parent-child relationships and ordering from `parent_unit_id` and `order_index` with no review-visible ordering mismatches.
- **SC-003**: Exported review patches contain every required audit field (`unit_id`, `field_path`, `old_value`, `new_value`, `reviewer_note`, `reviewer_decision`, `reviewed_at`) and do not duplicate full original regulation text unnecessarily.
- **SC-004**: A user can submit a runtime scenario through the workbench to a mocked or future 002 adapter and view a runtime judgment draft with citations, evidence, confidence, warnings, validation status, and review-status indicators when the response provides them.
- **SC-005**: All displayed runtime citations with available metadata show stable regulation unit ID, source document/version, article or clause number where available, retrieval provenance, and as-of-date basis; incomplete citations are visibly flagged.
- **SC-006**: Runtime trace display validation confirms that secrets, full prompts, provider payloads, and unnecessary sensitive raw text are not shown to reviewers.
- **SC-007**: Across structuring review and runtime scenario flows, draft outputs are labeled as non-final, and the feature produces no LLM calls, runtime logic, retrieval logic, rule execution, active `RulePack`, formal `RuleItem`, final `JudgmentResult`, or final compliance conclusion.

## Assumptions

- The review module consumes 001 `StructuringPipelineOutput` JSON as an existing contract; this feature does not define or run the 001 structuring pipeline.
- The final 002 Agent Runtime contract is not assumed to exist yet; runtime contracts in this feature are frontend-facing placeholders for UI development and mock validation.
- Reviewer identity, authentication, and authorization are provided by the surrounding workbench environment or later platform work; this feature records reviewer identity only when available.
- The first workbench scope is a desktop-oriented expert review and inspection experience; mobile optimization is not a primary success criterion for this feature.
- Sample 001 outputs and mocked runtime responses may be used for validation, but they must not be promoted to production runtime assets by this feature.
