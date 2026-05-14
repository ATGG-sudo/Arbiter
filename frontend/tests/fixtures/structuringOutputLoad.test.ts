import { describe, it, expect } from 'vitest'
import { loadStructuringOutput } from '../../src/validation/loadStructuringOutput'
import validFixture from '../../src/fixtures/structuring-output.valid.json'
import invalidFixture from '../../src/fixtures/structuring-output.invalid.json'

describe('loadStructuringOutput', () => {
  it('accepts a valid fixture', () => {
    const result = loadStructuringOutput(validFixture)
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.units).toHaveLength(10)
    }
  })

  it('rejects the invalid fixture with readable errors', () => {
    const result = loadStructuringOutput(invalidFixture)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.errors.length).toBeGreaterThan(0)
    }
  })

  it('rejects completely non-object input', () => {
    const result = loadStructuringOutput('not json')
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.errors.length).toBeGreaterThan(0)
    }
  })

  it('rejects null input', () => {
    const result = loadStructuringOutput(null)
    expect(result.success).toBe(false)
  })

  it('rejects missing required top-level fields', () => {
    const bad = { ...validFixture }
    delete (bad as any).document
    const result = loadStructuringOutput(bad)
    expect(result.success).toBe(false)
  })

  it('rejects mismatched document_id in validation_report', () => {
    const bad = structuredClone(validFixture)
    ;(bad as any).validation_report.document_id = 'mismatch'
    const result = loadStructuringOutput(bad)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.errors.some((e) => e.includes('document_id'))).toBe(true)
    }
  })

  it('rejects mismatched document_id in dependency_graph', () => {
    const bad = structuredClone(validFixture)
    ;(bad as any).dependency_graph.document_id = 'mismatch'
    const result = loadStructuringOutput(bad)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.errors.some((e) => e.includes('document_id'))).toBe(true)
    }
  })

  it('rejects mismatched unit document_id', () => {
    const bad = structuredClone(validFixture)
    ;(bad as any).units[0].document_id = 'mismatch'
    const result = loadStructuringOutput(bad)
    expect(result.success).toBe(false)
    if (!result.success) {
      expect(result.errors.some((e) => e.includes('document_id'))).toBe(true)
    }
  })
})
