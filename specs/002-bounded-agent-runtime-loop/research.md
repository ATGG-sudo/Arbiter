# Research: Bounded Agent Runtime Loop

## Decision: Use a bounded AgentLoop, not a deterministic workflow

**Rationale**: Spec002 exists to test Agent autonomy under runtime discipline.
The Agent must inspect current state, observations, reviewed assets, validation
feedback, available tools, and remaining budget before proposing the next
action. A fixed orchestration sequence would fail the core purpose even if it
produced the same no-matching-rule output.

**Alternatives considered**: A hard-coded sequence was rejected because it
removes Agent planning. Separate judgment and discovery workflows were rejected
because they hide the Agent's decision to shift reasoning context.

## Decision: Require `NextActionPlan` plus StepValidator before every tool call

**Rationale**: The Agent can plan, but only the runtime can execute. A
structured plan gives StepValidator a schema-backed object to approve or reject
and gives reviewers an auditable decision record.

**Alternatives considered**: Free-form tool requests were rejected because they
are difficult to validate, replay, or audit. Direct model tool execution was
rejected because it bypasses runtime boundaries.

## Decision: Keep Phase 1 tools local and reviewed-asset only

**Rationale**: Phase 1 must be reviewable and conservative. It may use
`UserInput`, `ScenarioInput`, active reviewed rules, reviewed structured
regulation context, local runtime artifacts, and local trace storage. This is
enough to prove the no-matching-rule path without adding web or raw-file risk.

**Alternatives considered**: Web search was deferred to a later optional
`WebEvidenceDiscoveryTool`. Raw PDF/Word parsing and 001 structuring were
rejected for Phase 1 because they belong to Admin-side workflows.

## Decision: Treat judgment and discovery as contexts inside one loop

**Rationale**: When the Agent observes `no_matching_rule`, it may decide to
query reviewed regulation context and generate exploratory draft material. That
choice should remain an Agent decision within the same bounded loop, not a
forced workflow branch.

**Alternatives considered**: Separate "judgment lane" and "discovery lane"
pipelines were rejected because they encourage rigid orchestration.

## Decision: Separate `RuleDraftCandidate` from `RuleItem`

**Rationale**: Draft rule material is useful for human review but unsafe as a
formal runtime basis. `RuleDraftCandidate` must be `needs_review`, inactive,
non-promoted, and incompatible with active `RulePack` without a later explicit
review and promotion spec.

**Alternatives considered**: Reusing `RuleItem` with a draft flag was rejected
because it creates accidental compatibility with active rule-pack paths.

## Decision: Use conservative `JudgmentDraft` validation for no matching rule

**Rationale**: If no reviewed rule matches, the runtime must not output
approved, final, pass, compliant, or equivalent statuses. The draft must require
human review, carry warnings, and have no formal basis rule IDs.

**Alternatives considered**: Producing a tentative positive or negative
compliance answer was rejected because reviewed rule coverage is insufficient.

## Decision: Use file-based local run storage for MVP

**Rationale**: `.arbiter/runs/<run_id>/` keeps the first runtime auditable
without introducing a database or production audit backend. JSON and JSONL
artifacts support manual inspection, replay, and later Spec003 or CLI
visualization.

**Alternatives considered**: A database was rejected as unnecessary for MVP.
In-memory-only trace was rejected because it cannot support audit or replay.

## Decision: Persist sanitized summaries by default

**Rationale**: Compliance scenarios, prompts, and provider payloads can contain
sensitive information. Default traces store IDs, summaries, validation status,
token counts, timing, and error summaries. Full prompts are allowed only when
`debug_mode = true`.

**Alternatives considered**: Full prompt logging by default was rejected for
sensitive-data risk. No model trace was rejected because budget enforcement and
audit need call summaries and token counts.

## Decision: Track token counts, defer cost estimation

**Rationale**: Token budget enforcement requires counts. Cost estimation depends
on provider pricing and can change over time, so it should not block the MVP.

**Alternatives considered**: Blocking MVP on cost calculation was rejected
because it adds drift-prone provider policy and pricing work to the runtime
contract.
