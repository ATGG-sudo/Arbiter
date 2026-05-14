import type { RuntimeScenarioInput, RuntimeJudgmentDraftView } from '../contracts/runtimeContracts'
import runtimeDraftFixture from '../fixtures/runtime-draft.mock.json'

export async function submitScenario(
  _input: RuntimeScenarioInput,
): Promise<RuntimeJudgmentDraftView> {
  // This is a mock adapter. It does not call any LLM, retrieval system,
  // vector search, rule execution, or 002 runtime logic.
  // It returns a static fixture response for UI development only.
  await new Promise((resolve) => setTimeout(resolve, 300))
  return runtimeDraftFixture as RuntimeJudgmentDraftView
}
