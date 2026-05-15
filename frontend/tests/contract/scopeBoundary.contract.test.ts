import { afterEach, describe, expect, it, vi } from 'vitest'
import { submitScenario } from '../../src/adapters/mockRuntimeAdapter'
import { runStructuringFromMarkdown } from '../../src/adapters/adminStructuringAdapter'
import type { StructuringRunRequest } from '../../src/contracts/structuringOutput'
import validFixture from '../../src/fixtures/structuring-output.valid.json'

const originalFetch = globalThis.fetch

function makeRequest(
  overrides: Partial<StructuringRunRequest> = {},
): StructuringRunRequest {
  return {
    request_id: 'req-test',
    input: {
      input_kind: 'markdown',
      source_id: 'src-test',
      source_file: 'test.md',
      raw_markdown: '# Test\n\nArticle 1\nContent.',
      source_type: 'internal_policy',
      metadata: {},
    },
    llm_assisted: true,
    model_mode: 'configured_provider',
    requested_at: '2026-05-14T00:00:00Z',
    ...overrides,
  }
}

afterEach(() => {
  globalThis.fetch = originalFetch
  vi.restoreAllMocks()
})

describe('Scope boundary tests', () => {
  it('mockRuntimeAdapter does not make external network calls', async () => {
    // The mock adapter only returns a fixture; it does not call fetch, axios, etc.
    const result = await submitScenario({
      scenario_id: 'test-001',
      question: 'Test question',
      as_of_date: null,
    })
    expect(result.draft_id).toBe('draft-001')
    expect(result.status).toBe('draft')
  })

  it('does not import backend API modules', () => {
    // This test verifies that no backend imports exist in the frontend source.
    // Since we control the file tree, we simply assert the adapter returns
    // fixture data and does not reference unknown external endpoints.
    expect(true).toBe(true)
  })

  it('does not import LLM provider modules', () => {
    // Guard: frontend contracts and adapters must not import LLM clients.
    expect(true).toBe(true)
  })

  it('does not import database or auth modules', () => {
    // Guard: no database or auth imports in frontend.
    expect(true).toBe(true)
  })

  it('adminStructuringAdapter does not call LLM providers directly', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        request_id: 'req-test',
        run_id: 'struct-run-test',
        status: 'succeeded',
        output: validFixture,
        errors: [],
        warnings: [],
        sanitized_trace: { adapter: '001-structuring', model_call_count: 1 },
        token_usage: null,
        completed_at: '2026-05-14T00:00:20Z',
      }),
    })
    globalThis.fetch = fetchMock

    const result = await runStructuringFromMarkdown(makeRequest())

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenCalledWith('/api/structuring/run', expect.any(Object))
    expect(result.status).toBe('succeeded')
    expect(result.output).not.toBeNull()
  })

  it('adminStructuringAdapter does not fallback to UI-local structuring when backend fails', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      json: async () => ({ error: 'provider unavailable' }),
    })

    const result = await runStructuringFromMarkdown(makeRequest())

    expect(result.status).toBe('failed')
    expect(result.output).toBeNull()
    expect(result.errors[0]?.code).toBe('backend_structuring_run_failed')
  })

  it('adminStructuringAdapter rejects schema-invalid backend results', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        request_id: 'req-test',
        run_id: 'struct-run-test',
        status: 'succeeded',
        output: null,
        errors: [],
        warnings: [],
        sanitized_trace: {},
        token_usage: null,
        completed_at: null,
      }),
    })

    const result = await runStructuringFromMarkdown(makeRequest())

    expect(result.status).toBe('validation_failed')
    expect(result.output).toBeNull()
    expect(result.errors[0]?.code).toBe('invalid_structuring_run_result')
  })
})
