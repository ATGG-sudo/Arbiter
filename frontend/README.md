# Arbiter Workbench UI (003)

Frontend-only expert workbench for reviewing Markdown-derived and JSON
`StructuringPipelineOutput` assets from 001 Regulation Structuring.

## Scope

- **US1 MVP (implemented)**: Send Markdown to the local 001 Admin structuring
  adapter, load 001-compatible JSON, review/edit draft structuring output, and
  export review artifacts or an integrated modified structuring review package.
- **US2/US3 (not implemented)**: Runtime scenario preview and trace inspection are mocked at the contract level only.

## Tech Stack

- Vite + React + TypeScript
- Zod for frontend validation mirror
- Vitest + Testing Library for unit/contract tests
- Playwright for smoke tests (requires system browser dependencies)

## Commands

```bash
npm install
npm run test      # Run Vitest contract/unit tests
npm run dev       # Start dev server
npx playwright test # Run smoke tests (requires system deps)
```

## Project Structure

```
src/
  contracts/        # Zod schemas and types (structuringOutput, reviewArtifacts, runtimeContracts)
  fixtures/         # Valid/invalid fixture JSON and mock runtime draft
  adapters/         # Admin structuring client and mock runtime adapter
  workbench/        # UI components and session state
  validation/       # JSON load validation and redaction helpers
  App.tsx           # Main app integration
tests/
  contract/         # Contract validation tests
  fixtures/         # Fixture load tests
  smoke/            # Playwright smoke tests
```

## Key Behaviors

- **Base output immutability**: Loaded JSON or Markdown-derived base output is frozen; all edits produce separate review artifacts.
- **Markdown intake**: Markdown is sent to `/api/structuring/run` as a
  `StructuringRunRequest`. The user can choose whether `llm_assisted` is true;
  the frontend never calls a model provider directly and never falls back to
  UI-local structuring when the Admin adapter fails.
- **Integrated export**: The integrated package keeps `base_output` unchanged
  and applies patches only to `merged_output`.
- **Patch consolidation**: Repeated unsaved edits to the same field produce a single latest-consolidated patch (not a sequence).
- **Validation**: Invalid JSON, empty Markdown, and unsupported file types are rejected with readable errors; no editable session is created.
