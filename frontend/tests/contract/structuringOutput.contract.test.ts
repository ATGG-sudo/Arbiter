import { describe, it, expect } from 'vitest'
import {
  StructuringPipelineOutput,
  StructuringRunRequest,
  StructuringRunResult,
} from '../../src/contracts/structuringOutput'
import validFixture from '../../src/fixtures/structuring-output.valid.json'
import invalidFixture from '../../src/fixtures/structuring-output.invalid.json'

describe('StructuringPipelineOutput Zod validation mirror', () => {
  it('accepts a valid fixture with 10 units', () => {
    const result = StructuringPipelineOutput.safeParse(validFixture)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.units).toHaveLength(10)
      expect(result.data.contract_version).toBe('v1')
    }
  })

  it('rejects invalid extraction_method', () => {
    const bad = structuredClone(validFixture) as any
    bad.extraction_provenance.extraction_method = 'magic'
    const result = StructuringPipelineOutput.safeParse(bad)
    expect(result.success).toBe(false)
  })

  it('rejects negative order_index', () => {
    const bad = structuredClone(validFixture) as any
    bad.units[0].order_index = -1
    const result = StructuringPipelineOutput.safeParse(bad)
    expect(result.success).toBe(false)
  })

  it('rejects empty original_text', () => {
    const bad = structuredClone(validFixture) as any
    bad.units[0].original_text = '   '
    const result = StructuringPipelineOutput.safeParse(bad)
    expect(result.success).toBe(false)
  })

  it('rejects missing required document fields', () => {
    const bad = structuredClone(validFixture) as any
    delete bad.document.document_id
    const result = StructuringPipelineOutput.safeParse(bad)
    expect(result.success).toBe(false)
  })

  it('rejects missing contract_version', () => {
    const bad = structuredClone(validFixture) as any
    bad.contract_version = ''
    const result = StructuringPipelineOutput.safeParse(bad)
    expect(result.success).toBe(false)
  })

  it('rejects invalid severity in validation findings', () => {
    const bad = structuredClone(validFixture) as any
    bad.validation_report.findings[0].severity = 'critical'
    const result = StructuringPipelineOutput.safeParse(bad)
    expect(result.success).toBe(false)
  })

  it('rejects invalid review_status', () => {
    const bad = structuredClone(validFixture) as any
    bad.units[0].review_status = 'pending'
    const result = StructuringPipelineOutput.safeParse(bad)
    expect(result.success).toBe(false)
  })

  it('rejects the invalid fixture', () => {
    const result = StructuringPipelineOutput.safeParse(invalidFixture)
    expect(result.success).toBe(false)
  })

  it('preserves defaults for optional fields', () => {
    const minimal = {
      contract_version: 'v1',
      extraction_provenance: {
        extraction_method: 'deterministic',
      },
      document: {
        document_id: 'doc-min',
        source_id: 'src-min',
        source_file: 'min.md',
        classification: {
          source_type: 'unknown',
        },
        temporal_metadata: {
          version_label: null,
        },
        parse_status: 'parsed',
        warnings: [],
        review_status: 'needs_review',
      },
      units: [],
      reference_candidates: [],
      dependency_graph: {
        graph_id: 'g-min',
        document_id: 'doc-min',
      },
      validation_report: {
        document_id: 'doc-min',
        summary: 'Minimal',
      },
    }
    const result = StructuringPipelineOutput.safeParse(minimal)
    expect(result.success).toBe(true)
  })
})

describe('StructuringRunRequest Zod validation', () => {
  it('accepts a valid run request', () => {
    const request = {
      request_id: 'req-001',
      input: {
        input_kind: 'markdown',
        source_id: 'src-policy-001',
        source_file: 'investment-policy.md',
        raw_markdown: '# Policy\n\nArticle 1\nContent.',
        source_type: 'internal_policy',
        metadata: { title: 'Investment Policy' },
      },
      llm_assisted: true,
      model_mode: 'configured_provider',
      requested_at: '2026-05-14T00:00:00Z',
    }
    const result = StructuringRunRequest.safeParse(request)
    expect(result.success).toBe(true)
  })

  it('rejects empty raw_markdown', () => {
    const request = {
      request_id: 'req-001',
      input: {
        input_kind: 'markdown',
        source_id: 'src-001',
        source_file: 'policy.md',
        raw_markdown: '',
        source_type: 'internal_policy',
        metadata: {},
      },
      llm_assisted: true,
      model_mode: 'configured_provider',
      requested_at: '2026-05-14T00:00:00Z',
    }
    const result = StructuringRunRequest.safeParse(request)
    expect(result.success).toBe(false)
  })

  it('rejects invalid model_mode', () => {
    const request = {
      request_id: 'req-001',
      input: {
        input_kind: 'markdown',
        source_id: 'src-001',
        source_file: 'policy.md',
        raw_markdown: '# Policy',
        source_type: 'internal_policy',
        metadata: {},
      },
      llm_assisted: true,
      model_mode: 'openai_direct',
      requested_at: '2026-05-14T00:00:00Z',
    }
    const result = StructuringRunRequest.safeParse(request)
    expect(result.success).toBe(false)
  })
})

describe('StructuringRunResult Zod validation', () => {
  it('accepts a succeeded result with output', () => {
    const resultObj = {
      request_id: 'req-001',
      run_id: 'struct-run-001',
      status: 'succeeded',
      output: validFixture,
      errors: [],
      warnings: [],
      sanitized_trace: {
        adapter: '001-structuring',
        model_call_count: 1,
      },
      token_usage: {
        prompt_tokens: 100,
        completion_tokens: 50,
        total_tokens: 150,
      },
      completed_at: '2026-05-14T00:00:20Z',
    }
    const result = StructuringRunResult.safeParse(resultObj)
    expect(result.success).toBe(true)
  })

  it('accepts a validation_failed result without output', () => {
    const resultObj = {
      request_id: 'req-001',
      run_id: 'struct-run-001',
      status: 'validation_failed',
      output: null,
      errors: [{ code: 'empty_markdown', message: 'Empty input' }],
      warnings: [],
      sanitized_trace: {},
      token_usage: null,
      completed_at: null,
    }
    const result = StructuringRunResult.safeParse(resultObj)
    expect(result.success).toBe(true)
  })

  it('rejects invalid status', () => {
    const resultObj = {
      request_id: 'req-001',
      run_id: 'struct-run-001',
      status: 'partial_success',
      output: null,
      errors: [],
      warnings: [],
      sanitized_trace: {},
      token_usage: null,
      completed_at: null,
    }
    const result = StructuringRunResult.safeParse(resultObj)
    expect(result.success).toBe(false)
  })

  it('rejects a succeeded result without output', () => {
    const resultObj = {
      request_id: 'req-001',
      run_id: 'struct-run-001',
      status: 'succeeded',
      output: null,
      errors: [],
      warnings: [],
      sanitized_trace: {},
      token_usage: null,
      completed_at: null,
    }
    const result = StructuringRunResult.safeParse(resultObj)
    expect(result.success).toBe(false)
  })
})
