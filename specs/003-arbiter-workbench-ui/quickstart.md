# Quickstart: Arbiter Workbench UI

This quickstart describes how the completed 003 MVP should be validated after
implementation tasks are generated and completed.

## Preconditions

- Use fixture or exported JSON conforming to 001 `StructuringPipelineOutput`.
- Do not run 001 pipeline code as part of 003 validation.
- Do not require 002 Agent Runtime availability.
- Do not use backend, database, live LLM, retrieval, rule execution, or API
  route commands for this feature.

## Expected Validation Flow

1. Install the frontend test/runtime dependencies defined by the implementation.
2. Run the frontend test suite.
3. Start the local workbench.
4. Load a valid `StructuringPipelineOutput` fixture.
5. Confirm the unit tree preserves `parent_unit_id` and `order_index`.
6. Open the document metadata panel and inspect title, `document_number`,
   classification, dates, temporal metadata, warnings, validation findings, and
   `review_status`.
7. Select a unit and inspect original text, normalized text, evidence,
   validation findings, and semantic draft fields.
8. Edit one semantic draft field and export a `StructuringReviewPatch`.
9. Make repeated unsaved edits to the same target and `field_path`, then verify
   export behavior clearly indicates a patch sequence or latest consolidated
   patch.
10. Record one review decision for a document, unit, semantic draft, reference
    candidate, dependency edge, or curation note.
11. Add one `AssetCurationRecord` for a note, candidate rule hint, scenario
    example, ambiguity case, or dependency issue.
12. Submit a `RuntimeScenarioInput` through a mocked adapter.
13. Inspect `RuntimeJudgmentDraftView`, `RuntimeCitationView`,
    `RuntimeEvidenceView`, and `RuntimeTraceView`.
14. Verify runtime output remains labeled draft/non-final.

## Negative Checks

- Invalid `StructuringPipelineOutput` JSON is rejected with readable validation
  feedback and no editable review session is created.
- The loaded source JSON is not mutated in place.
- Missing citation identifiers are flagged as incomplete.
- Runtime trace display blocks secrets, full prompts, provider payloads, and
  unnecessary sensitive raw text.
- Placeholder runtime UI contracts are not treated as backend or domain-level
  002 schemas.
- No active `RulePack`, formal `RuleItem`, final `JudgmentResult`, runtime-safe
  reviewed asset, or final compliance conclusion is generated.
- PDF and Word files are not accepted as direct inputs.

## Suggested Commands

The planned frontend package should provide:

```bash
npm install
npm run test
npm run dev
```

Backend, database, live LLM, retrieval, rule execution, 002 runtime, and API
route commands are not part of this feature.
