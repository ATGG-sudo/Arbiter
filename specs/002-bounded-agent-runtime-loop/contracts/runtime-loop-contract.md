# Contract: Bounded Agent Runtime Loop

**Contract status**: Planning contract  
**Scope**: Phase 1 bounded Agent Runtime, local reviewed assets, local run
storage, conservative judgment drafts, and human review tasks  
**Out of scope**: Web search, raw PDF parsing, raw Word parsing, 001
structuring, writing reviewed regulation context, active rule writes, draft
promotion, final compliance conclusions, production storage, and Spec003 UI
implementation

## Operation

`run_agent_loop(scenario_input, runtime_options) -> AgentRunResult`

Required behavior:
- Start only after `ScenarioInput` exists.
- Let the Agent propose `NextActionPlan` in each round.
- Validate every plan through StepValidator before tool execution.
- Execute only allowed Phase 1 tools.
- Reject forbidden tools and actions with trace records.
- Enforce `max_rounds`, `max_tool_calls`, and token budget.
- Save local artifacts under `.arbiter/runs/<run_id>/`.
- Return conservative output when reviewed rule coverage is insufficient.

The operation is intentionally not a deterministic workflow. The examples below
show valid contract shapes, not a required execution order.

## Request

```json
{
  "schema_version": "runtime-loop.v1",
  "scenario_input": {
    "schema_version": "scenario-input.v1",
    "scenario_id": "scenario-001",
    "normalized_question": "Can this investment proceed under the current reviewed rules?",
    "business_subject": "private_fund",
    "action_type": "investment_approval",
    "amount": {
      "value": 1000000,
      "currency": "CNY"
    },
    "date_fields": {
      "submitted_date": "2026-05-14"
    },
    "as_of_date": "2026-05-14",
    "known_facts": {
      "example": "review fixture only"
    },
    "missing_facts": [],
    "validation_status": "pending"
  },
  "runtime_options": {
    "runtime_mode": "phase1_local",
    "max_rounds": 3,
    "max_tool_calls": 8,
    "max_token_budget": null,
    "web_search_enabled": false,
    "debug_mode": false,
    "allowed_tools": [
      "validate_scenario_input",
      "inspect_missing_facts",
      "check_rule_coverage",
      "load_reviewed_rule_pack",
      "query_reviewed_regulation_context",
      "generate_rule_draft_candidate",
      "record_rule_draft_candidate",
      "validate_judgment_draft",
      "record_agent_trace",
      "create_human_review_task"
    ]
  }
}
```

## NextActionPlan

The Agent must produce a structured plan before any tool call.

```json
{
  "schema_version": "next-action-plan.v1",
  "action_id": "action-001",
  "run_id": "run-001",
  "round_index": 1,
  "selected_tool": "check_rule_coverage",
  "purpose": "Determine whether active reviewed rules cover the scenario.",
  "expected_input": {
    "scenario_id": "scenario-001",
    "as_of_date": "2026-05-14"
  },
  "expected_output": {
    "coverage_status": "matched | no_matching_rule"
  },
  "why_this_action": "Reviewed rule coverage is required before any formal basis can be used.",
  "current_assumption": "The scenario has enough facts for a coverage check.",
  "risk_notes": [
    "Rule coverage may be insufficient."
  ],
  "requires_validation": true,
  "stop_if_success": null,
  "stop_if_failure": "Return validation feedback to Agent.",
  "validation_status": "pending",
  "rejection_reason": null,
  "created_at": "2026-05-14T00:00:00Z"
}
```

StepValidator required behavior:
- Accept only Phase 1 allowed tools.
- Reject forbidden action names and forbidden intent.
- Reject draft rule use as formal basis.
- Reject actions that exceed remaining rounds, tool calls, or token budget.
- Reject actions that require unavailable reviewed assets.
- Record `accepted` or `rejected` status and reason in trace.

## Allowed Tool Contracts

### validate_scenario_input

Input: `ScenarioInput`

Output:

```json
{
  "schema_version": "scenario-validation.v1",
  "scenario_id": "scenario-001",
  "validation_status": "valid",
  "missing_facts": [],
  "warnings": []
}
```

### inspect_missing_facts

Input: `scenario_id`, current facts, and observations.

Output: missing fact list and warnings. Missing facts are reviewable
observations, not fabricated values.

### check_rule_coverage

Input: `scenario_id`, active reviewed rule pack IDs, and `as_of_date`.

Output:

```json
{
  "schema_version": "rule-coverage-report.v1",
  "coverage_status": "no_matching_rule",
  "matched_rule_ids": [],
  "checked_rule_pack_ids": ["reviewed-rule-pack-001"],
  "reason": "No active reviewed rule matched the scenario facts.",
  "confidence": 0.82,
  "created_at": "2026-05-14T00:01:00Z"
}
```

### load_reviewed_rule_pack

Loads only active reviewed rule packs. Draft, `needs_review`, missing-review,
and inactive packs are not formal basis.

### query_reviewed_regulation_context

Queries reviewed structured regulation context only. It must not run 001,
parse raw files, or write reviewed context.

### generate_rule_draft_candidate

Generates exploratory rule material only when reviewed context supports it.
Output must be `RuleDraftCandidate` with `review_status = needs_review` and
`human_review_required = true`.

### record_rule_draft_candidate

Appends candidates to `rule_draft_candidates.jsonl`. This does not activate,
promote, or write active rules.

### validate_judgment_draft

Validates conservative output rules:
- No draft IDs in `formal_basis_rule_ids`.
- If `rule_coverage_status = no_matching_rule`, status is not approved, final,
  pass, compliant, or equivalent.
- If no reviewed rule matches, `human_review_required = true`.
- Citations use reviewed context references where available.

### record_agent_trace

Records sanitized trace entries. Full prompts are saved only when
`debug_mode = true`.

### create_human_review_task

Creates a `HumanReviewTask` linked to the judgment draft and exploratory draft
candidate IDs.

## Forbidden Actions

StepValidator must reject:

- `parse_pdf`
- `parse_docx`
- `run_001_structuring_pipeline`
- `activate_rule_pack`
- `promote_rule_draft`
- `write_active_rule`
- `write_reviewed_regulation_context`
- `produce_final_compliance_conclusion`
- `use_draft_rule_as_formal_basis`
- `call_web_search`

Forbidden rejection example:

```json
{
  "schema_version": "step-validation.v1",
  "action_id": "action-002",
  "validation_status": "rejected",
  "rejection_reason": "Phase 1 forbids call_web_search.",
  "stop_reason": "forbidden_action_rejected"
}
```

## RuleDraftCandidate

```json
{
  "schema_version": "rule-draft-candidate.v1",
  "draft_rule_id": "draft-rule-001",
  "source_run_id": "run-001",
  "scenario_id": "scenario-001",
  "trigger_reason": "no_matching_rule",
  "draft_title": "Exploratory investment approval rule candidate",
  "draft_condition": "Reviewed context suggests a threshold or approval condition may apply.",
  "draft_action": "Require human review before any runtime use.",
  "draft_obligation": null,
  "draft_exception": null,
  "source_evidence": [
    {
      "context_id": "reviewed-context-001",
      "unit_id": "unit-001",
      "citation": "Reviewed context citation"
    }
  ],
  "generated_rationale": "No active reviewed rule matched; reviewed context may support a future reviewed rule.",
  "confidence": 0.64,
  "review_status": "needs_review",
  "created_at": "2026-05-14T00:02:00Z",
  "human_review_required": true
}
```

Required behavior:
- Not a `RuleItem`.
- Not compatible with active `RulePack`.
- Not formal judgment basis.

## JudgmentDraft

```json
{
  "schema_version": "judgment-draft.v1",
  "judgment_id": "judgment-001",
  "run_id": "run-001",
  "scenario_id": "scenario-001",
  "judgment_status": "insufficient_rule_coverage",
  "rule_coverage_status": "no_matching_rule",
  "summary": "No active reviewed rule matched this scenario. Human review is required.",
  "reasoning_summary": "Reviewed rule coverage was checked and no formal basis rule was found. Reviewed context may support exploratory draft material.",
  "formal_basis_rule_ids": [],
  "exploratory_rule_draft_ids": ["draft-rule-001"],
  "citations": [
    {
      "context_id": "reviewed-context-001",
      "unit_id": "unit-001",
      "as_of_date": "2026-05-14"
    }
  ],
  "warnings": [
    "Insufficient reviewed rule coverage.",
    "Exploratory draft rules are not formal basis."
  ],
  "validation_report": {
    "status": "valid",
    "errors": [],
    "warnings": []
  },
  "human_review_required": true,
  "created_at": "2026-05-14T00:03:00Z"
}
```

## HumanReviewTask

```json
{
  "schema_version": "human-review-task.v1",
  "task_id": "review-task-001",
  "run_id": "run-001",
  "scenario_id": "scenario-001",
  "review_reason": "No active reviewed rule matched the scenario.",
  "related_judgment_draft_id": "judgment-001",
  "related_rule_draft_candidate_ids": ["draft-rule-001"],
  "priority": "normal",
  "status": "open",
  "created_at": "2026-05-14T00:04:00Z"
}
```

## AgentRunResult

```json
{
  "schema_version": "agent-run-result.v1",
  "run_id": "run-001",
  "scenario_id": "scenario-001",
  "stop_reason": "human_review_required",
  "final_status": "needs_review",
  "judgment_draft_id": "judgment-001",
  "human_review_task_ids": ["review-task-001"],
  "local_run_path": ".arbiter/runs/run-001/"
}
```

## Local Run Store Contract

Required files:

```text
.arbiter/runs/<run_id>/
|-- run.json
|-- user_input.redacted.json
|-- scenario_input.json
|-- runtime_state.json
|-- next_action_plans.jsonl
|-- coverage_report.json
|-- steps.jsonl
|-- tool_calls.jsonl
|-- model_calls.jsonl
|-- token_usage.jsonl
|-- rule_draft_candidates.jsonl
|-- judgment_draft.json
|-- validation_report.json
\-- human_review_tasks.jsonl
```

Persistence requirements:
- Every artifact includes `schema_version`.
- JSONL files append one complete object per line.
- Sensitive raw input is not saved by default.
- Full prompts are saved only when `debug_mode = true`.
- Replay uses saved artifacts and does not call the model.
