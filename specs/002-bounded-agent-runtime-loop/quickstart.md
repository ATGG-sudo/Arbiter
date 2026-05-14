# Quickstart: Bounded Agent Runtime Loop

This quickstart describes how the completed Spec002 MVP should be validated
after implementation tasks are generated and completed. It is not an
implementation script.

## Preconditions

- A `ScenarioInput` fixture is available.
- At least one active reviewed rule pack fixture is available, but it does not
  match the scenario.
- Reviewed structured regulation context fixture is available for optional
  exploratory draft generation.
- Local run storage is enabled under `.arbiter/runs/<run_id>/`.
- `web_search_enabled = false`.
- `debug_mode = false` unless a local debug validation explicitly enables it.

Do not use web search, raw PDF parsing, raw Word parsing, 001 structuring,
automatic rule activation, automatic rule promotion, or final compliance
conclusion commands for this feature.

## Expected Validation Flow

1. Convert `UserInput` into `ScenarioInput`.
2. Start `AgentRun` and initial `AgentRuntimeState`.
3. Let the Agent propose a `NextActionPlan`.
4. Pass the plan through StepValidator.
5. If accepted, execute only the selected allowed tool and update state.
6. If rejected, record the rejection and return the reason to the Agent.
7. Continue within `max_rounds = 3`, `max_tool_calls = 8`, and token budget.
8. Verify the Agent can observe `no_matching_rule` from reviewed rule coverage.
9. Verify the Agent may query reviewed regulation context after that
   observation.
10. Verify any `RuleDraftCandidate` is exploratory, `needs_review`, inactive,
    non-promoted, and never formal basis.
11. Validate `JudgmentDraft` so it requires human review and has no formal basis
    rule IDs when no reviewed rule matches.
12. Create a `HumanReviewTask`.
13. Stop with `human_review_required` when judgment draft and review task were
    produced, or `no_matching_rule` if the run stops earlier.
14. Inspect `.arbiter/runs/<run_id>/` artifacts.
15. Replay from saved artifacts without model calls.

## Negative Checks

- A `NextActionPlan` selecting `call_web_search` is rejected.
- A `NextActionPlan` selecting `parse_pdf`, `parse_docx`, or
  `run_001_structuring_pipeline` is rejected.
- A `NextActionPlan` attempting `activate_rule_pack`, `promote_rule_draft`, or
  `write_active_rule` is rejected.
- A `NextActionPlan` attempting `write_reviewed_regulation_context` is
  rejected.
- A `JudgmentDraft` with draft IDs in `formal_basis_rule_ids` is invalid.
- A `JudgmentDraft` with `approved`, `final`, `pass`, or `compliant` status
  while `rule_coverage_status = no_matching_rule` is invalid.
- Missing reviewed citations or temporal basis are warnings or human review
  reasons, not silently inferred facts.
- Raw user input and full prompts are absent from default local artifacts.
- Budget exhaustion produces the matching stop reason.

## Suggested Future Commands

The planned implementation should expose repository-native validation commands
similar to:

```bash
PYTHONPATH=src ./.venv/bin/python -m pytest tests/agent_runtime -q
```

If a CLI entry point is later added, it should support a local fixture run and a
replay mode without re-calling the model. The CLI must still preserve Agent
autonomy; it must not replace the AgentLoop with a fixed orchestration sequence.
