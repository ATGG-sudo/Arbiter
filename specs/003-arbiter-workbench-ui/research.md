# Research: Arbiter Workbench UI

## Decision: Frontend-only workbench for MVP

**Rationale**: The feature must curate 001 outputs immediately and prepare
runtime-facing screens without implementing backend services, 002 runtime, rule
execution, retrieval, or LLM calls. A frontend-only workbench can load fixture
JSON, validate contracts, show review screens, and export artifacts while
keeping execution boundaries clear.

The implementation plan uses a TypeScript + Vite + React frontend with Zod as a
frontend validation mirror for loaded JSON. This is the smallest concrete
browser-app baseline that supports tree navigation, document metadata review,
editable review surfaces, JSON import/export, mock adapter flows, and focused
frontend tests without creating backend scope. The canonical 001 contract
remains the existing Python/Pydantic schema.

**Alternatives considered**:
- Backend-backed review service: rejected because storage, services, and
  authentication are out of scope.
- Runtime-integrated UI: rejected because 002 does not exist and this feature
  must not implement runtime logic.

## Decision: Use fixture/exported `StructuringPipelineOutput` as input

**Rationale**: The MVP must work without running 001. Accepting fixture or
exported JSON conforming to `StructuringPipelineOutput` lets reviewers validate
the workbench with stable samples while the 001 implementation continues
independently.

**Alternatives considered**:
- Invoke the 001 pipeline from the workbench: rejected because this feature must
  not implement or depend on pipeline execution.
- Accept raw PDF/DOCX: rejected because raw document parsing is explicitly out
  of scope.

## Decision: Export review and curation artifacts separately

**Rationale**: Source JSON must remain unchanged. Separate
`StructuringReviewPatch`, `StructuringReviewDecision`, and
`AssetCurationRecord` artifacts preserve auditability, reviewer intent, source
linkage, and optional reviewer identity when available without promoting drafts
into formal runtime assets.

**Alternatives considered**:
- Mutate loaded source JSON in place: rejected because it hides audit history.
- Generate active rules from review notes: rejected because active `RulePack`
  and formal `RuleItem` creation are out of scope.

## Decision: Make repeated unsaved edit export behavior explicit

**Rationale**: Multiple unsaved edits to the same target and `field_path` can
otherwise hide audit context. The workbench must make clear whether export
produces a patch sequence or the latest consolidated patch so reviewers know
what audit record they are creating.

**Alternatives considered**:
- Silently overwrite local edits: rejected because it loses review context.
- Force only one export style in the feature spec: rejected because the product
  requirement only needs the behavior to be clear and auditable.

## Decision: Runtime-facing screens use mock/future adapters only

**Rationale**: 002 Agent Runtime does not exist. Placeholder screens can still
shape the future user experience by rendering scenario input, judgment drafts,
citations, evidence, and sanitized traces from mocked data or a future adapter
boundary.

**Alternatives considered**:
- Implement runtime execution behind the UI: rejected as a direct scope
  violation.
- Omit runtime-facing screens entirely: rejected because the workbench must
  prepare for future 002 integration.

## Decision: Placeholder runtime contracts remain replaceable

**Rationale**: `RuntimeScenarioInput`, `RuntimeJudgmentDraftView`,
`RuntimeCitationView`, `RuntimeEvidenceView`, and `RuntimeTraceView` are
frontend-facing placeholders. They must not become backend or domain-level 002
schemas, and they must remain replaceable once 002 finalizes its contracts.

**Alternatives considered**:
- Treat placeholder runtime contracts as final schemas: rejected because 002 has
  not finalized its runtime contracts.
- Leave runtime screens untyped: rejected because the UI needs stable mocked
  data for planning and testing.

## Decision: Validation is contract-first and explicit

**Rationale**: The workbench must reject invalid 001 JSON, flag incomplete
citations, preserve missing temporal/source data as incomplete, and prevent
placeholder runtime contracts from being mistaken for final 002 schemas. Any
frontend validation of `StructuringPipelineOutput` is only a UI-side mirror of
the canonical 001 Python/Pydantic contract.

**Alternatives considered**:
- Best-effort rendering of malformed data: rejected because reviewers could
  confuse fabricated or incomplete fields with reviewed evidence.
- Create an editable review session after validation failure: rejected because
  schema-incompatible inputs must not become reviewable content.
