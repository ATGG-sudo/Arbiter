import { describe, it, expect } from 'vitest'
import {
  RuntimeScenarioInput,
  RuntimeJudgmentDraftView,
  RuntimeCitationView,
  RuntimeEvidenceView,
  RuntimeTraceView,
} from '../../src/contracts/runtimeContracts'

describe('RuntimeScenarioInput contract', () => {
  it('accepts a valid scenario input', () => {
    const input = {
      scenario_id: 'scenario-001',
      question: 'Can this investment proceed under the current policy?',
      structured_fields: {
        transaction_type: 'investment',
        amount: 'example only',
      },
      as_of_date: '2026-05-13',
    }
    const result = RuntimeScenarioInput.safeParse(input)
    expect(result.success).toBe(true)
  })

  it('rejects empty question', () => {
    const input = {
      scenario_id: 'scenario-001',
      question: '',
    }
    const result = RuntimeScenarioInput.safeParse(input)
    expect(result.success).toBe(false)
  })
})

describe('RuntimeJudgmentDraftView contract', () => {
  it('accepts a valid judgment draft', () => {
    const draft = {
      draft_id: 'draft-001',
      scenario_id: 'scenario-001',
      status: 'draft',
      summary: 'Mock judgment draft for UI inspection only.',
      confidence: 0.72,
      warnings: ['Mock response'],
      validation_status: 'needs_review',
      human_review_required: true,
      citations: [],
      evidence: [],
      trace: {
        trace_id: 'trace-001',
        steps: [],
        redaction_warnings: [],
      },
    }
    const result = RuntimeJudgmentDraftView.safeParse(draft)
    expect(result.success).toBe(true)
  })

  it('rejects invalid status', () => {
    const draft = {
      draft_id: 'draft-001',
      scenario_id: 'scenario-001',
      status: 'final' as any,
      summary: 'Summary',
      validation_status: 'needs_review',
      human_review_required: true,
      citations: [],
      evidence: [],
    }
    const result = RuntimeJudgmentDraftView.safeParse(draft)
    expect(result.success).toBe(false)
  })
})

describe('RuntimeCitationView contract', () => {
  it('accepts a valid citation', () => {
    const citation = {
      citation_id: 'citation-001',
      unit_id: 'unit-001',
      document_id: 'doc-001',
      source_version: 'v1',
      article_or_clause: 'Article 1',
      provenance: 'mock-adapter',
      as_of_date: '2026-05-13',
    }
    const result = RuntimeCitationView.safeParse(citation)
    expect(result.success).toBe(true)
  })

  it('rejects missing unit_id', () => {
    const citation = {
      citation_id: 'citation-001',
      unit_id: '' as any,
      document_id: 'doc-001',
    }
    const result = RuntimeCitationView.safeParse(citation)
    expect(result.success).toBe(false)
  })
})

describe('RuntimeEvidenceView contract', () => {
  it('accepts a valid evidence view', () => {
    const evidence = {
      evidence_id: 'evidence-001',
      unit_id: 'unit-001',
      excerpt: 'Bounded evidence excerpt.',
      dependency_context: ['edge-001'],
      provenance: 'mock-adapter',
      as_of_date: '2026-05-13',
    }
    const result = RuntimeEvidenceView.safeParse(evidence)
    expect(result.success).toBe(true)
  })
})

describe('RuntimeTraceView contract', () => {
  it('accepts a valid trace view', () => {
    const trace = {
      trace_id: 'trace-001',
      steps: [
        {
          step_id: 'step-001',
          label: 'Mock adapter returned draft',
          status: 'completed',
        },
      ],
      redaction_warnings: [],
    }
    const result = RuntimeTraceView.safeParse(trace)
    expect(result.success).toBe(true)
  })

  it('rejects step with empty label', () => {
    const trace = {
      trace_id: 'trace-001',
      steps: [
        {
          step_id: 'step-001',
          label: '' as any,
          status: 'completed',
        },
      ],
      redaction_warnings: [],
    }
    const result = RuntimeTraceView.safeParse(trace)
    expect(result.success).toBe(false)
  })
})
