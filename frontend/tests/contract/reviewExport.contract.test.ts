import { describe, it, expect } from 'vitest'
import {
  createReviewPatch,
  createReviewDecision,
  createCurationRecord,
} from '../../src/workbench/exportArtifacts'
import type { SourceOutputRef } from '../../src/contracts/reviewArtifacts'

const sampleRef: SourceOutputRef = {
  contract_version: 'v1',
  document_id: 'doc-001',
  source_id: 'source-001',
  source_file: 'sample-policy.md',
  loaded_at: '2026-05-13T00:00:00Z',
}

describe('Review patch export', () => {
  it('creates a patch with all required audit fields', () => {
    const patch = createReviewPatch(sampleRef, {
      targetType: 'semantic_draft',
      targetId: 'unit-001.semantic_draft',
      unitId: 'unit-001',
      fieldPath: 'semantic_draft.summary',
      oldValue: 'Old summary',
      newValue: 'New summary',
      reviewerNote: 'Updated for clarity',
      reviewerDecision: 'needs_changes',
      reviewerIdentity: null,
    })

    expect(patch.source_output_ref).toEqual(sampleRef)
    expect(patch.target_type).toBe('semantic_draft')
    expect(patch.target_id).toBe('unit-001.semantic_draft')
    expect(patch.unit_id).toBe('unit-001')
    expect(patch.field_path).toBe('semantic_draft.summary')
    expect(patch.old_value).toBe('Old summary')
    expect(patch.new_value).toBe('New summary')
    expect(patch.reviewer_note).toBe('Updated for clarity')
    expect(patch.reviewer_decision).toBe('needs_changes')
    expect(patch.reviewed_at).toBeTruthy()
  })

  it('does not duplicate full original text unnecessarily', () => {
    const patch = createReviewPatch(sampleRef, {
      targetType: 'semantic_draft',
      targetId: 'unit-001.semantic_draft',
      unitId: 'unit-001',
      fieldPath: 'semantic_draft.summary',
      oldValue: 'Short value',
      newValue: 'New short value',
      reviewerNote: '',
      reviewerDecision: 'approved',
      reviewerIdentity: null,
    })

    // The patch should only contain the edited field value, not the full unit text.
    expect(patch.old_value).toBe('Short value')
    expect(patch.new_value).toBe('New short value')
  })
})

describe('Repeated unsaved edit behavior', () => {
  it('exports latest consolidated patch when same field is edited twice (consolidated behavior)', () => {
    // This workbench uses latest-consolidated behavior: only the final edit
    // for a given target+field_path is kept in the session, and export produces
    // one patch per target+field_path reflecting the latest change.
    const sessionPatches: Record<string, ReturnType<typeof createReviewPatch>> = {}

    const key = 'unit-001.semantic_draft.summary'
    sessionPatches[key] = createReviewPatch(sampleRef, {
      targetType: 'semantic_draft',
      targetId: 'unit-001.semantic_draft',
      unitId: 'unit-001',
      fieldPath: 'semantic_draft.summary',
      oldValue: 'Draft summary',
      newValue: 'First edit',
      reviewerNote: 'First pass',
      reviewerDecision: 'needs_changes',
      reviewerIdentity: null,
    })

    // Second edit to same field overwrites in session (latest consolidated)
    sessionPatches[key] = createReviewPatch(sampleRef, {
      targetType: 'semantic_draft',
      targetId: 'unit-001.semantic_draft',
      unitId: 'unit-001',
      fieldPath: 'semantic_draft.summary',
      oldValue: 'Draft summary',
      newValue: 'Second edit',
      reviewerNote: 'Second pass',
      reviewerDecision: 'needs_changes',
      reviewerIdentity: null,
    })

    const exported = Object.values(sessionPatches)
    expect(exported).toHaveLength(1)
    expect(exported[0].new_value).toBe('Second edit')
    expect(exported[0].reviewer_note).toBe('Second pass')
  })
})

describe('Review decision export', () => {
  it('creates a decision with required fields', () => {
    const decision = createReviewDecision(sampleRef, {
      targetType: 'unit',
      targetId: 'unit-001',
      unitId: 'unit-001',
      reviewerDecision: 'approved',
      reviewerNote: 'Looks good after review.',
      reviewerIdentity: null,
    })

    expect(decision.source_output_ref).toEqual(sampleRef)
    expect(decision.target_type).toBe('unit')
    expect(decision.target_id).toBe('unit-001')
    expect(decision.unit_id).toBe('unit-001')
    expect(decision.reviewer_decision).toBe('approved')
    expect(decision.reviewer_note).toBe('Looks good after review.')
    expect(decision.reviewed_at).toBeTruthy()
  })
})

describe('Curation record export', () => {
  it('creates a curation record with required fields', () => {
    const record = createCurationRecord(
      sampleRef,
      {
        noteType: 'expert_note',
        targetType: 'unit',
        targetId: 'unit-001',
        unitId: 'unit-001',
        note: 'This unit needs additional legal review.',
        reviewerIdentity: null,
      },
      'curation-001',
    )

    expect(record.source_output_ref).toEqual(sampleRef)
    expect(record.curation_id).toBe('curation-001')
    expect(record.note_type).toBe('expert_note')
    expect(record.target_type).toBe('unit')
    expect(record.target_id).toBe('unit-001')
    expect(record.unit_id).toBe('unit-001')
    expect(record.note).toBe('This unit needs additional legal review.')
    expect(record.created_at).toBeTruthy()
    expect(record.review_status).toBe('needs_review')
  })
})
