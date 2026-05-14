# Feature Specification: Bounded Agent Runtime Loop

**Feature Branch**: `002-bounded-agent-runtime-loop`  
**Created**: 2026-05-14  
**Status**: Draft  
**Input**: User description: "Design Arbiter spec002 as a bounded compliance judgment Agent Runtime Loop. Do not implement code yet."

Spec002 defines the Arbiter bounded compliance judgment Agent Runtime. It is not
a fixed deterministic workflow. The Agent decides the next action at each
runtime round from the current `ScenarioInput`, runtime state, prior
observations, reviewed rules, reviewed regulation context, validation feedback,
allowed tools, and remaining budget. The runtime enforces discipline: tool
boundaries, StepValidator approval, budgets, audit trace, conservative judgment
rules, and human review gates.

The MVP proves one complete acceptance path: no active reviewed rule matches a
scenario. That path is described as expected runtime behavior, not as a
hard-coded sequence. Phase 1 uses only local reviewed assets and local run
artifacts. Web search, raw PDF/Word parsing, 001 structuring, automatic rule
activation, automatic promotion, and final compliance conclusions are out of
scope.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Agent Chooses Bounded Runtime Actions (Priority: P1)

As a runtime operator, I can start an AgentLoop from an available
`ScenarioInput`, and the Agent can autonomously propose a structured
`NextActionPlan` in each round while the runtime validates, executes, rejects,
or records the action according to allowed tools, budgets, and safety gates.

**Why this priority**: This is the defining behavior. If the runtime collapses
into a predefined sequence, it is not a real Agent Runtime.

**Independent Test**: Start a run with a sample `ScenarioInput` and verify that
each round records an Agent-proposed `NextActionPlan`, StepValidator decision,
runtime state update, and trace entry before any tool execution.

**Acceptance Scenarios**:

1. **Given** a valid `ScenarioInput` and available reviewed assets, **When** the
   AgentLoop starts, **Then** the Agent proposes a structured `NextActionPlan`
   rather than executing a tool directly.
2. **Given** an Agent-proposed action uses an allowed Phase 1 tool and stays
   within remaining budgets, **When** StepValidator accepts it, **Then** the
   runtime executes the tool and updates `AgentRuntimeState`.
3. **Given** an Agent proposes a forbidden action such as `call_web_search`,
   `parse_pdf`, `activate_rule_pack`, or `promote_rule_draft`, **When**
   StepValidator evaluates it, **Then** the runtime rejects the action, records
   the rejection, and returns the reason to the Agent for the next decision.
4. **Given** remaining rounds, tool calls, or token budget are exhausted,
   **When** the Agent proposes another action, **Then** the runtime blocks the
   action and stops with the relevant budget stop reason.

---

### User Story 2 - Produce Conservative Output When No Reviewed Rule Matches (Priority: P1)

As a compliance reviewer, I can submit a scenario for runtime judgment and, when
no active reviewed rule matches, receive a conservative `JudgmentDraft`,
optional exploratory `RuleDraftCandidate`, and `HumanReviewTask` without any
final compliance conclusion.

**Why this priority**: The MVP acceptance path validates the runtime's core
review gate: insufficient reviewed rule coverage must force human review.

**Independent Test**: Run a scenario against reviewed rule packs that have no
matching active reviewed rule and verify that output is `needs_review`, uses no
draft rule as formal basis, and creates a human review task.

**Acceptance Scenarios**:

1. **Given** active reviewed rules do not match the `ScenarioInput`, **When**
   the Agent observes `no_matching_rule`, **Then** the runtime records a
   `RuleCoverageReport` with `coverage_status = no_matching_rule`.
2. **Given** no reviewed rule matches, **When** the Agent produces a
   `JudgmentDraft`, **Then** `human_review_required = true`,
   `formal_basis_rule_ids = []`, and `judgment_status` is `needs_review` or
   `insufficient_rule_coverage`.
3. **Given** reviewed regulation context may support a possible future rule,
   **When** the Agent chooses discovery behavior, **Then** it may generate a
   `RuleDraftCandidate` that is exploratory, `needs_review`, not active, not
   promoted, and not usable as formal judgment basis.
4. **Given** a `JudgmentDraft` requires review, **When** the run stops, **Then**
   the runtime records a `HumanReviewTask` linked to the judgment draft and any
   exploratory draft candidates.

---

### User Story 3 - Preserve Auditable Local Run Records (Priority: P2)

As a developer or reviewer, I can inspect a completed local run and replay the
decision record from saved artifacts without re-calling the model.

**Why this priority**: Bounded autonomy is only reviewable if every decision,
validation result, tool call, model call summary, token count, and stop reason
is persisted consistently.

**Independent Test**: Complete a no-matching-rule run and inspect the local run
store for stable JSON/JSONL artifacts sharing the same `run_id` and
`schema_version`.

**Acceptance Scenarios**:

1. **Given** a run is started, **When** each round completes or validation
   fails, **Then** `next_action_plans.jsonl`, `steps.jsonl`,
   `tool_calls.jsonl`, `model_calls.jsonl`, `token_usage.jsonl`, and
   `runtime_state.json` are updated.
2. **Given** sensitive raw user text is present, **When** local artifacts are
   saved, **Then** raw input is not saved by default and only a redacted
   snapshot may be stored.
3. **Given** `debug_mode = false`, **When** model calls are traced, **Then**
   full prompts are not saved; only sanitized summaries and token counts are
   stored.
4. **Given** a reviewer opens saved artifacts later, **When** replay is
   requested, **Then** the saved action plans, observations, traces, and final
   artifacts are sufficient to reconstruct the run without a model call.

---

### User Story 4 - Enforce Phase 1 Runtime Boundaries (Priority: P2)

As a system maintainer, I can verify that Phase 1 runtime uses only local,
reviewed inputs and cannot reach web search, raw file parsing, 001 structuring,
rule promotion, or final conclusion paths.

**Why this priority**: The Agent may plan, but runtime authority must stay
bounded and conservative.

**Independent Test**: Submit prohibited `NextActionPlan` values and verify that
StepValidator rejects them, records trace entries, and prevents tool execution.

**Acceptance Scenarios**:

1. **Given** Phase 1 has `web_search_enabled = false`, **When** the Agent
   selects web search, **Then** StepValidator rejects the action.
2. **Given** the Agent proposes raw PDF/Word parsing or 001 structuring, **When**
   StepValidator evaluates the action, **Then** it rejects and records the
   forbidden action.
3. **Given** the Agent proposes using a draft rule as formal basis, activating
   a rule pack, promoting a draft, or writing active rules, **When**
   StepValidator evaluates the action, **Then** it rejects and records the
   violation.

### Edge Cases

- StepValidator rejects an otherwise allowed tool because required input is
  missing, invalid, or inconsistent with current `AgentRuntimeState`.
- The Agent repeatedly proposes invalid or forbidden actions until
  `max_rounds` is exhausted.
- Reviewed rule packs are available but none match the scenario.
- Reviewed regulation context is unavailable, insufficient, stale, or lacks
  stable citations.
- The Agent generates a draft rule candidate without enough reviewed context
  support.
- A judgment draft includes draft rule IDs in `formal_basis_rule_ids`.
- A final-looking status such as `approved`, `final`, `pass`, or `compliant`
  appears when `rule_coverage_status = no_matching_rule`.
- Token usage is unavailable from a provider response; the run records an
  explicit warning and preserves available counts.
- Debug mode is enabled for local troubleshooting; full prompt logging is then
  allowed only under the same `run_id` and must remain local and explicit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Spec002 MUST define a bounded Agent Runtime that operates in
  rounds and lets the Agent propose the next action at each round.
- **FR-002**: The runtime MUST NOT hard-code a rigid sequence such as validate,
  coverage check, context query, draft generation, and output judgment.
- **FR-003**: Each round MUST require the Agent to produce a structured
  `NextActionPlan` before any tool can be executed.
- **FR-004**: `NextActionPlan` MUST include `action_id`, `run_id`,
  `round_index`, `selected_tool`, `purpose`, `expected_input`,
  `expected_output`, `why_this_action`, `current_assumption`, `risk_notes`,
  `requires_validation`, `stop_if_success`, `stop_if_failure`,
  `validation_status`, `rejection_reason`, and `created_at`.
- **FR-005**: The Agent MUST NOT directly execute tools. The runtime MUST pass
  every `NextActionPlan` through StepValidator.
- **FR-006**: StepValidator MUST approve only allowed tools whose inputs,
  runtime mode, reviewed-asset requirements, and budgets are valid.
- **FR-007**: If StepValidator rejects an action, the runtime MUST record the
  rejection in trace, update `AgentRuntimeState`, and return the rejection
  reason to the Agent for another decision if budget remains.
- **FR-008**: Phase 1 allowed runtime tools are
  `validate_scenario_input`, `inspect_missing_facts`,
  `check_rule_coverage`, `load_reviewed_rule_pack`,
  `query_reviewed_regulation_context`, `generate_rule_draft_candidate`,
  `record_rule_draft_candidate`, `validate_judgment_draft`,
  `record_agent_trace`, and `create_human_review_task`.
- **FR-009**: Phase 1 MUST explicitly forbid `parse_pdf`, `parse_docx`,
  `run_001_structuring_pipeline`, `activate_rule_pack`,
  `promote_rule_draft`, `write_active_rule`,
  `write_reviewed_regulation_context`,
  `produce_final_compliance_conclusion`, `use_draft_rule_as_formal_basis`, and
  `call_web_search`.
- **FR-010**: The runtime MUST enforce `max_rounds = 3` by default,
  `max_tool_calls = 8` by default, configurable `max_token_budget`,
  `web_search_enabled = false`, and `debug_mode = false`.
- **FR-011**: The runtime MUST maintain `AgentRuntimeState` and update it after
  every validated tool call, validation rejection, warning, or stop condition.
- **FR-012**: `AgentRuntimeState` MUST include `run_id`, `scenario_id`,
  `current_round`, `remaining_rounds`, `remaining_tool_calls`,
  `remaining_token_budget`, `allowed_tools`, `completed_actions`,
  `observations`, `rule_coverage_status`, `reviewed_context_status`,
  `generated_draft_rule_ids`, `judgment_draft_id`,
  `human_review_required`, `stop_reason`, `validation_errors`, and `warnings`.
- **FR-013**: The runtime MUST support `UserInput` to `ScenarioInput`
  conversion as a pre-AgentLoop boundary.
- **FR-014**: `ScenarioInput` MUST include `scenario_id`,
  `normalized_question`, `business_subject`, `action_type`, `amount`,
  `date_fields`, `as_of_date`, `known_facts`, `missing_facts`, and
  `validation_status`.
- **FR-015**: The Agent MAY choose judgment behavior and discovery behavior
  inside the same AgentLoop; these MUST NOT be modeled as separate rigid
  workflows.
- **FR-016**: If no reviewed rule matches, the Agent MUST NOT produce a final
  positive or negative compliance conclusion.
- **FR-017**: If `rule_coverage_status = no_matching_rule`, `JudgmentDraft`
  MUST use `human_review_required = true`, `formal_basis_rule_ids = []`, and
  `judgment_status = needs_review` or `insufficient_rule_coverage`.
- **FR-018**: `JudgmentDraft.formal_basis_rule_ids` MUST NOT contain draft rule
  IDs.
- **FR-019**: `JudgmentDraft.exploratory_rule_draft_ids` MAY contain
  `RuleDraftCandidate` IDs.
- **FR-020**: `RuleDraftCandidate` MUST always be `needs_review`,
  `human_review_required = true`, not active, not promoted, and not compatible
  with active `RulePack` without explicit human review and a later promotion
  spec.
- **FR-021**: `RuleDraftCandidate` MUST be clearly separate from `RuleItem` and
  MUST NOT be usable as formal judgment basis.
- **FR-022**: The runtime MUST produce a `HumanReviewTask` when a judgment draft
  requires human review in the MVP no-matching-rule path.
- **FR-023**: The runtime MUST define stop reasons: `completed`,
  `no_matching_rule`, `human_review_required`, `max_rounds_exceeded`,
  `max_tool_calls_exceeded`, `max_token_budget_exceeded`,
  `validation_failed`, `model_error`, `tool_error`,
  `forbidden_action_rejected`, and `cancelled`.
- **FR-024**: The MVP no-matching-rule path SHOULD usually stop with
  `human_review_required` when a `JudgmentDraft` and `HumanReviewTask` are
  produced, or `no_matching_rule` when the run stops before those artifacts are
  produced.
- **FR-025**: The MVP local run store MUST use `.arbiter/runs/<run_id>/`.
- **FR-026**: Local run artifacts MUST use stable file names: `run.json`,
  `user_input.redacted.json`, `scenario_input.json`, `runtime_state.json`,
  `next_action_plans.jsonl`, `coverage_report.json`, `steps.jsonl`,
  `tool_calls.jsonl`, `model_calls.jsonl`, `token_usage.jsonl`,
  `rule_draft_candidates.jsonl`, `judgment_draft.json`,
  `validation_report.json`, and `human_review_tasks.jsonl`.
- **FR-027**: Every local run artifact MUST include `schema_version`.
- **FR-028**: Sensitive raw input MUST NOT be saved by default; a redacted
  snapshot MAY be saved.
- **FR-029**: Audit and debug artifacts MUST share the same `run_id`.
- **FR-030**: Replay MUST be possible from saved artifacts without re-calling
  the model.
- **FR-031**: `ModelCallTrace` MUST save provider, model, prompt contract
  version, input and output summaries, token usage, latency, status, and error
  summary.
- **FR-032**: Full prompts MUST NOT be saved by default and MAY be saved only
  when `debug_mode = true`.
- **FR-033**: `TokenUsage` MUST support token counts for provider, model,
  prompt tokens, completion tokens, total tokens, reasoning tokens, cached
  tokens, and call ID. Cost estimation is optional and MUST NOT block MVP.
- **FR-034**: `RuntimeValidationReport` MUST capture input, step, rule
  coverage, citation, temporal, draft rule, and output validation results plus
  errors, warnings, and human review reasons.
- **FR-035**: Trace output MUST be consumable later by spec003 or CLI
  visualization.
- **FR-036**: Phase 1 MUST NOT use web search, raw PDF parsing, raw Word
  parsing, 001 structuring, automatic rule activation, automatic rule
  promotion, or final compliance conclusions.

### Constitution Alignment *(mandatory for Arbiter features)*

- **CA-001**: Feature scope is Agent Runtime. It consumes reviewed rule packs,
  reviewed regulation context, `ScenarioInput`, and local runtime artifacts.
  It does not parse raw regulation files or run Admin structuring.
- **CA-002**: Runtime MUST reject draft, `needs_review`, or missing-review
  regulation assets as formal judgment basis unless a separate test mode is
  explicitly defined outside the Phase 1 production path.
- **CA-003**: Model use in Agent planning MUST go through `LLMClient` /
  `ModelProvider`. Provider settings stay outside business logic, and model
  output is schema-gated through `NextActionPlan` and output validation.
- **CA-004**: `ScenarioInput`, `JudgmentDraft`, citations, and reviewed context
  MUST preserve `as_of_date`, source version, effective date, expiration date,
  and amendment/source-version relation where available.
- **CA-005**: `JudgmentDraft` citations MUST use stable reviewed regulation
  context references where available. Free-text-only citation labels are
  insufficient for reviewed basis.
- **CA-006**: Core runtime inputs, outputs, traces, tool calls, model calls,
  token usage, validation reports, and human review tasks MUST be structured
  JSON/Pydantic-style contracts.
- **CA-007**: Sensitive data, raw prompts, raw user input, secrets, provider
  payloads, traces, and debug mode MUST have explicit local redaction and
  logging behavior.
- **CA-008**: User-facing compliance output remains a `JudgmentDraft` requiring
  human review when reviewed rule coverage is insufficient. It MUST NOT replace
  final compliance decisions.

### Key Entities *(include if feature involves data)*

- **UserInput**: Raw user-submitted question and context before normalization.
- **ScenarioInput**: Structured runtime input available before AgentLoop
  begins.
- **AgentRuntimeState**: Mutable bounded runtime state used by the Agent and
  updated by the runtime after each decision or validation event.
- **NextActionPlan**: Agent-proposed structured plan for the next runtime
  action.
- **RuleCoverageReport**: Result of checking active reviewed rule coverage.
- **RuleDraftCandidate**: Exploratory draft rule material created only for human
  review when no reviewed rule matches and reviewed context supports a possible
  rule.
- **JudgmentDraft**: Conservative runtime output that may summarize reasoning
  and warnings but does not become a final compliance conclusion.
- **AgentRun**: Run-level metadata, limits, allowed tools, final status, and
  debug mode.
- **AgentStepTrace**: Sanitized step-level trace for decisions, validations,
  tool calls, model calls, and summaries.
- **ToolCallTrace**: Tool execution trace with schema versions, summaries,
  timing, status, and errors.
- **ModelCallTrace**: Model call trace with summaries, prompt contract version,
  token usage, latency, status, and errors.
- **TokenUsage**: Provider/model token counts for audit and budget enforcement.
- **RuntimeValidationReport**: Consolidated validation report for the run.
- **HumanReviewTask**: Runtime output contract for required human review.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `UserInput` can be converted into `ScenarioInput` before
  AgentLoop starts.
- **SC-002**: AgentLoop starts only after `ScenarioInput` is available and
  records `AgentRun` metadata.
- **SC-003**: In each round, the Agent can autonomously propose a structured
  `NextActionPlan`.
- **SC-004**: Runtime validates every `NextActionPlan` before execution and
  rejects forbidden actions.
- **SC-005**: The Agent can choose allowed tools such as scenario validation,
  missing-fact inspection, reviewed rule coverage checks, reviewed context
  query, draft candidate generation, judgment validation, trace recording, and
  human review task creation.
- **SC-006**: The Agent can observe `no_matching_rule` from reviewed rule
  coverage.
- **SC-007**: The Agent can query reviewed regulation context after observing
  `no_matching_rule`.
- **SC-008**: The Agent can generate a `RuleDraftCandidate` when reviewed
  context supports exploratory rule material.
- **SC-009**: `RuleDraftCandidate` is recorded as `needs_review`, cannot become
  an active rule, and cannot be used as formal judgment basis.
- **SC-010**: `JudgmentDraft` is produced with `human_review_required = true`
  when no reviewed rule matches.
- **SC-011**: `JudgmentDraft` uses no draft rule as formal basis.
- **SC-012**: `HumanReviewTask` is produced and linked to the judgment draft and
  exploratory draft candidates.
- **SC-013**: All steps, action plans, tool calls, model calls, validation
  results, token usage, output drafts, and stop reason are saved locally.
- **SC-014**: Trace artifacts can be consumed later by spec003 or CLI
  visualization.
- **SC-015**: Runtime enforces `max_rounds`, `max_tool_calls`, token budget,
  allowed tools, validation gates, and stop reason.
- **SC-016**: Phase 1 does not use web search, raw PDF/Word parsing, 001
  structuring, automatic rule activation, automatic promotion, or final
  compliance conclusions.
- **SC-017**: Implementation planning preserves Agent autonomy and does not
  collapse the runtime into a deterministic workflow.

## Assumptions

- Spec001 provides reviewed structured regulation context only after human
  review; Spec002 does not call Spec001 or parse raw files.
- Active reviewed rules and reviewed context exist as local artifacts or
  repository-native fixtures suitable for Phase 1 validation.
- The first implementation may use a mock model provider for Agent planning
  tests, but the planning contract remains model-provider agnostic.
- Phase 1 local storage is file-based; production storage, remote audit
  backends, and multi-user concurrency are outside MVP.
- Spec003 may later display run traces and human review tasks, but Spec002 owns
  the runtime output contracts that produce them.
