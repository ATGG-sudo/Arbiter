import { describe, it, expect } from 'vitest'
import { StructuringPipelineOutput } from '../../src/contracts/structuringOutput'
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
