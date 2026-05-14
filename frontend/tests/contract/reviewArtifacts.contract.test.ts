import { describe, it, expect } from 'vitest'
import {
  StructuringReviewPatch,
  StructuringReviewDecision,
  AssetCurationRecord,
  SourceOutputRef,
} from '../../src/contracts/reviewArtifacts'

const sampleRef: SourceOutputRef = {
  contract_version: 'v1',
  document_id: 'doc-001',
  source_id: 'source-001',
  source_file: 'sample-policy.md',
  loaded_at: '2026-05-13T00:00:00Z',
}

describe('StructuringReviewPatch contract', () => {
  it('accepts a valid patch', () => {
    const patch = {
      source_output_ref: sampleRef,
      target_type: 'semantic_draft',
      target_id: 'unit-001.semantic_draft',
      unit_id: 'unit-001',
      field_path: 'units[0].semantic_draft.obligations[0]',
      old_value: 'draft obligation text',
      new_value: 'reviewed obligation text',
      reviewer_note: 'Clarified wording against source evidence.',
      reviewer_decision: 'needs_changes',
      reviewed_at: '2026-05-13T00:10:00Z',
      reviewer_identity: 'reviewer-id-if-available',
    }
    const result = StructuringReviewPatch.safeParse(patch)
    expect(result.success).toBe(true)
  })

  it('rejects missing required source_output_ref fields', () => {
    const badRef = { ...sampleRef, document_id: '' }
    const patch = {
      source_output_ref: badRef,
      target_type: 'semantic_draft',
      target_id: 't-1',
      field_path: 'fp',
      old_value: 'old',
      new_value: 'new',
      reviewer_decision: 'approved',
      reviewed_at: '2026-05-13T00:00:00Z',
    }
    const result = StructuringReviewPatch.safeParse(patch)
    expect(result.success).toBe(false)
  })

  it('rejects invalid target_type', () => {
    const patch = {
      source_output_ref: sampleRef,
      target_type: 'invalid_target' as any,
      target_id: 't-1',
      field_path: 'fp',
      old_value: 'old',
      new_value: 'new',
      reviewer_decision: 'approved',
      reviewed_at: '2026-05-13T00:00:00Z',
    }
    const result = StructuringReviewPatch.safeParse(patch)
    expect(result.success).toBe(false)
  })

  it('rejects invalid reviewer_decision', () => {
    const patch = {
      source_output_ref: sampleRef,
      target_type: 'unit',
      target_id: 't-1',
      field_path: 'fp',
      old_value: 'old',
      new_value: 'new',
      reviewer_decision: 'maybe' as any,
      reviewed_at: '2026-05-13T00:00:00Z',
    }
    const result = StructuringReviewPatch.safeParse(patch)
    expect(result.success).toBe(false)
  })

  it('allows optional unit_id to be null', () => {
    const patch = {
      source_output_ref: sampleRef,
      target_type: 'document',
      target_id: 'doc-001',
      unit_id: null,
      field_path: 'document.title',
      old_value: 'Old Title',
      new_value: 'New Title',
      reviewer_decision: 'needs_changes',
      reviewed_at: '2026-05-13T00:00:00Z',
    }
    const result = StructuringReviewPatch.safeParse(patch)
    expect(result.success).toBe(true)
  })
})

describe('StructuringReviewDecision contract', () => {
  it('accepts a valid decision', () => {
    const decision = {
      source_output_ref: sampleRef,
      target_type: 'dependency_edge',
      target_id: 'edge-001',
      unit_id: 'unit-001',
      reviewer_decision: 'needs_more_evidence',
      reviewer_note: 'Target unit is ambiguous.',
      reviewed_at: '2026-05-13T00:12:00Z',
      reviewer_identity: null,
    }
    const result = StructuringReviewDecision.safeParse(decision)
    expect(result.success).toBe(true)
  })

  it('rejects missing target_id', () => {
    const decision = {
      source_output_ref: sampleRef,
      target_type: 'unit',
      target_id: '' as any,
      reviewer_decision: 'approved',
      reviewed_at: '2026-05-13T00:00:00Z',
    }
    const result = StructuringReviewDecision.safeParse(decision)
    expect(result.success).toBe(false)
  })
})

describe('AssetCurationRecord contract', () => {
  it('accepts a valid curation record', () => {
    const record = {
      source_output_ref: sampleRef,
      curation_id: 'curation-001',
      note_type: 'scenario_example',
      target_type: 'unit',
      target_id: 'unit-001',
      unit_id: 'unit-001',
      note: 'Useful future scenario: investment approval threshold review.',
      created_at: '2026-05-13T00:15:00Z',
      review_status: 'needs_review',
      reviewer_identity: null,
    }
    const result = AssetCurationRecord.safeParse(record)
    expect(result.success).toBe(true)
  })

  it('rejects invalid note_type', () => {
    const record = {
      source_output_ref: sampleRef,
      curation_id: 'curation-001',
      note_type: 'random_note' as any,
      note: 'Some note',
      created_at: '2026-05-13T00:00:00Z',
      review_status: 'needs_review',
    }
    const result = AssetCurationRecord.safeParse(record)
    expect(result.success).toBe(false)
  })

  it('allows optional target fields to be absent', () => {
    const record = {
      source_output_ref: sampleRef,
      curation_id: 'curation-002',
      note_type: 'expert_note',
      note: 'General observation about the document.',
      created_at: '2026-05-13T00:00:00Z',
      review_status: 'needs_review',
    }
    const result = AssetCurationRecord.safeParse(record)
    expect(result.success).toBe(true)
  })
})
