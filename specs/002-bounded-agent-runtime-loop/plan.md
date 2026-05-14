# Implementation Plan: Bounded Agent Runtime Loop

**Branch**: `002-bounded-agent-runtime-loop` | **Date**: 2026-05-14 | **Spec**: `specs/002-bounded-agent-runtime-loop/spec.md`
**Input**: Feature specification from `/specs/002-bounded-agent-runtime-loop/spec.md`

## Summary

Build a bounded compliance judgment Agent Runtime Loop. The Agent proposes the
next action during each round through `NextActionPlan`; the runtime validates
that proposal through StepValidator before any tool execution. The runtime
enforces allowed tools, forbidden actions, budgets, validation gates, audit
trace, local run storage, conservative judgment rules, and human review tasks.

The MVP proves the no-active-reviewed-rule-matches path without turning it into
a fixed workflow. The Agent may choose expected actions such as scenario
validation, missing-fact inspection, reviewed rule coverage checking, reviewed
context query, exploratory draft generation, judgment validation, trace
recording, and human review task creation. These are acceptable Agent choices,
not a hard-coded sequence.

## Technical Context

**Language/Version**: Python 3.11+ with Pydantic-style runtime contracts  
**Primary Dependencies**: Existing `LLMClient` / `ModelProvider` boundary for Agent planning, Pydantic schemas, local file JSON/JSONL persistence, pytest with mock model and tool fixtures  
**Storage**: File-based local run store under `.arbiter/runs/<run_id>/`; no production database in MVP  
**Testing**: pytest unit and integration-style fixture tests for schema validation, StepValidator, forbidden actions, budgets, no-matching-rule run path, local artifacts, replay, redaction, and conservative judgment validation  
**Target Platform**: Local or controlled server-side runtime environment  
**Project Type**: Python runtime library with optional CLI/dev entry points for local runs and replay  
**Performance Goals**: Complete a representative no-matching-rule MVP run within the default `max_rounds = 3` and `max_tool_calls = 8`; persist all audit artifacts before returning final status  
**Constraints**: Agent autonomy in planning; runtime discipline in execution; Phase 1 uses only local `UserInput`, `ScenarioInput`, active reviewed rules, reviewed structured regulation context, local artifacts, and local trace store; no web search, raw PDF/Word parsing, 001 structuring, automatic rule activation/promotion, or final compliance conclusion  
**Scale/Scope**: Single-run MVP focused on the `no_matching_rule` branch, one local run directory per run, token counts only, cost estimation optional

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Admin / Runtime Separation**: PASS. This is an Agent Runtime feature. It
  consumes `ScenarioInput`, active reviewed rule packs, reviewed regulation
  context, and local runtime artifacts. It does not parse raw regulation files,
  run the 001 structuring pipeline, write reviewed regulation context, activate
  rule packs, or promote draft rules.
- **Unified Model Access**: PASS. Agent planning model calls must go through
  `LLMClient` / `ModelProvider`, use structured `NextActionPlan` output, and
  include mock-provider coverage. The runtime, not the model, executes tools.
- **Structured Data Contracts**: PASS. Core contracts are `UserInput`,
  `ScenarioInput`, `AgentRuntimeState`, `NextActionPlan`,
  `RuleCoverageReport`, `RuleDraftCandidate`, `JudgmentDraft`, `AgentRun`,
  `AgentStepTrace`, `ToolCallTrace`, `ModelCallTrace`, `TokenUsage`,
  `RuntimeValidationReport`, and `HumanReviewTask`.
- **Temporal Regulation Basis**: PASS. `ScenarioInput`, reviewed context,
  citations, and `JudgmentDraft` preserve `as_of_date`, effective date,
  expiration date, source version, and amendment/source-version relation where
  available. Missing temporal facts become warnings or human review reasons.
- **Citation and Evidence**: PASS. Reviewed regulation citations require stable
  reviewed context references. Draft rule candidates may be exploratory
  evidence for human review, but cannot be formal basis. Free-text-only
  citations are insufficient for formal reviewed basis.
- **Runtime Review Gates**: PASS. Runtime rejects draft, `needs_review`, or
  missing-review-status regulation assets as formal judgment basis. No matching
  reviewed rule forces conservative `JudgmentDraft` output and human review.
- **Secure Configuration**: PASS. No real secrets, private scenarios, or
  provider payloads are hard-coded. Debug mode is false by default, and full
  prompt logging is allowed only when explicitly enabled locally.
- **Auditable but Sanitized Logging**: PASS. Local trace records IDs,
  validation status, rejection reasons, budget counters, stop reason, model and
  tool summaries, token counts, citation checks, temporal checks, draft status,
  and human review reasons. Raw input and full prompts are not saved by
  default.
- **Code Quality and Testability**: PASS. Required tests target schema
  validation, StepValidator rejection/approval, budget stops, forbidden actions,
  no-matching-rule behavior, draft-rule separation, conservative judgment
  validation, local run artifacts, replay, token accounting, and redaction.

## Project Structure

### Documentation (this feature)

```text
specs/002-bounded-agent-runtime-loop/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
\-- contracts/
    \-- runtime-loop-contract.md
```

`tasks.md` is intentionally not generated by this `/speckit-plan` stage.

### Source Code (repository root)

```text
src/
\-- arbiter/
    |-- agent_runtime/
    |   |-- loop.py
    |   |-- state.py
    |   |-- validation.py
    |   |-- tools.py
    |   |-- storage.py
    |   \-- replay.py
    |-- schemas/
    |   \-- agent_runtime.py
    \-- llm/
        \-- ... existing LLMClient / ModelProvider boundary ...

tests/
\-- agent_runtime/
    |-- fixtures/
    |-- test_agent_runtime_schemas.py
    |-- test_next_action_validation.py
    |-- test_forbidden_actions.py
    |-- test_budget_enforcement.py
    |-- test_no_matching_rule_path.py
    |-- test_judgment_draft_validation.py
    |-- test_rule_draft_candidate_boundary.py
    |-- test_local_run_store.py
    |-- test_replay_artifacts.py
    \-- test_trace_redaction.py
```

**Structure Decision**: Keep the implementation in a Runtime-owned
`arbiter.agent_runtime` package and a dedicated schema module. Do not add code
under Admin structuring, active rule promotion, web search, raw-file parsing, or
Spec003 UI.

## Phase 0 Research

Completed in `specs/002-bounded-agent-runtime-loop/research.md`.

Key decisions:
- Use one bounded AgentLoop with runtime-enforced StepValidator rather than a
  deterministic workflow.
- Treat judgment and discovery as reasoning contexts inside the same loop.
- Keep Phase 1 tools local and explicitly forbid web/raw parsing/promotion.
- Persist one local file-based run store per `run_id`.
- Require conservative judgment validation when reviewed rule coverage is
  insufficient.
- Record token counts but leave cost estimation optional for MVP.

## Phase 1 Design & Contracts

Completed artifacts:
- `specs/002-bounded-agent-runtime-loop/data-model.md`
- `specs/002-bounded-agent-runtime-loop/contracts/runtime-loop-contract.md`
- `specs/002-bounded-agent-runtime-loop/quickstart.md`

The design defines runtime data contracts, StepValidator behavior, allowed and
forbidden Phase 1 tools, local run storage, trace contracts, conservative
judgment validation, draft rule boundaries, and human review output. It does
not define web search, raw document parsing, 001 structuring, rule activation,
rule promotion, final compliance conclusions, production storage, or Spec003 UI
implementation.

## Post-Design Constitution Check

PASS. The Phase 1 artifacts preserve Admin/Runtime separation, keep all runtime
decisions schema-backed and auditable, route model planning through the shared
model boundary, protect temporal and citation requirements, reject draft assets
as formal basis, enforce human review when reviewed rule coverage is
insufficient, and keep Phase 1 local and reviewable.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
