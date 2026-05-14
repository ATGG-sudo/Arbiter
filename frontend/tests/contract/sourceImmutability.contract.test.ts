import { describe, it, expect } from 'vitest'
import { loadStructuringOutput } from '../../src/validation/loadStructuringOutput'
import validFixture from '../../src/fixtures/structuring-output.valid.json'
import type { SessionState } from '../../src/workbench/reviewSession'
import { recordPatch } from '../../src/workbench/reviewSession'
import { deepFreeze } from '../../src/workbench/sessionState'

describe('Source JSON immutability', () => {
  it('loadStructuringOutput does not mutate the input object', () => {
    const original = structuredClone(validFixture)
    loadStructuringOutput(validFixture)
    expect(validFixture).toEqual(original)
  })

  it('session sourceOutput is deeply frozen and cannot be mutated at top level', () => {
    const result = loadStructuringOutput(validFixture)
    expect(result.success).toBe(true)
    if (!result.success) return

    const session: SessionState = {
      sourceOutput: deepFreeze(structuredClone(result.data)),
      sourceOutputRef: {
        contract_version: result.data.contract_version,
        document_id: result.data.document.document_id,
        source_id: result.data.document.source_id,
        source_file: 'test.json',
        loaded_at: new Date().toISOString(),
      },
      inputKind: 'structuring_output_json',
      sourceMarkdown: null,
      patchMap: new Map(),
      decisions: [],
      curationRecords: [],
    }

    // Top-level mutation blocked
    expect(() => {
      ;(session.sourceOutput as any).contract_version = 'tampered'
    }).toThrow()
  })

  it('session sourceOutput is deeply frozen and cannot be mutated at nested levels', () => {
    const result = loadStructuringOutput(validFixture)
    expect(result.success).toBe(true)
    if (!result.success) return

    const session: SessionState = {
      sourceOutput: deepFreeze(structuredClone(result.data)),
      sourceOutputRef: {
        contract_version: result.data.contract_version,
        document_id: result.data.document.document_id,
        source_id: result.data.document.source_id,
        source_file: 'test.json',
        loaded_at: new Date().toISOString(),
      },
      inputKind: 'structuring_output_json',
      sourceMarkdown: null,
      patchMap: new Map(),
      decisions: [],
      curationRecords: [],
    }

    // Nested document mutation blocked
    expect(() => {
      ;(session.sourceOutput as any).document.title = 'tampered'
    }).toThrow()

    // Nested unit mutation blocked
    expect(() => {
      ;(session.sourceOutput as any).units[0].original_text = 'tampered'
    }).toThrow()

    // Deep semantic_draft mutation blocked
    expect(() => {
      ;(session.sourceOutput as any).units[0].semantic_draft.summary = 'tampered'
    }).toThrow()

    // Array mutation blocked
    expect(() => {
      ;(session.sourceOutput as any).units[0].semantic_draft.obligations.push('tampered')
    }).toThrow()
  })

  it('recordPatch does not mutate the original session', () => {
    const result = loadStructuringOutput(validFixture)
    expect(result.success).toBe(true)
    if (!result.success) return

    const session: SessionState = {
      sourceOutput: deepFreeze(structuredClone(result.data)),
      sourceOutputRef: {
        contract_version: result.data.contract_version,
        document_id: result.data.document.document_id,
        source_id: result.data.document.source_id,
        source_file: 'test.json',
        loaded_at: new Date().toISOString(),
      },
      inputKind: 'structuring_output_json',
      sourceMarkdown: null,
      patchMap: new Map(),
      decisions: [],
      curationRecords: [],
    }

    const newSession = recordPatch(
      session,
      'unit-001',
      'semantic_draft',
      'unit-001.semantic_draft.summary',
      'semantic_draft.summary',
      'Old summary',
      'New summary',
      'Note',
      'needs_changes',
    )

    // Original session should be unchanged
    expect(session.patchMap.size).toBe(0)
    expect(newSession.patchMap.size).toBe(1)
    expect(session.sourceOutput).toEqual(newSession.sourceOutput)
  })
})
