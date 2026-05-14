import type {
  StructuringReviewPatch,
  StructuringReviewDecision,
  AssetCurationRecord,
  IntegratedStructuringReviewPackage,
  SourceOutputRef,
  ReviewTargetType,
  ReviewDecision,
  CurationNoteType,
} from '../contracts/reviewArtifacts'
import type { StructuringPipelineOutput } from '../contracts/structuringOutput'
import type { SessionState } from './reviewSession'

export interface PatchInput {
  targetType: ReviewTargetType
  targetId: string
  unitId: string | null
  fieldPath: string
  oldValue: unknown
  newValue: unknown
  reviewerNote: string
  reviewerDecision: ReviewDecision
  reviewerIdentity: string | null
}

export function createReviewPatch(
  sourceOutputRef: SourceOutputRef,
  input: PatchInput,
  reviewedAt: string = new Date().toISOString(),
): StructuringReviewPatch {
  return {
    source_output_ref: sourceOutputRef,
    target_type: input.targetType,
    target_id: input.targetId,
    unit_id: input.unitId,
    field_path: input.fieldPath,
    old_value: input.oldValue,
    new_value: input.newValue,
    reviewer_note: input.reviewerNote,
    reviewer_decision: input.reviewerDecision,
    reviewed_at: reviewedAt,
    reviewer_identity: input.reviewerIdentity,
  }
}

export interface DecisionInput {
  targetType: ReviewTargetType
  targetId: string
  unitId: string | null
  reviewerDecision: ReviewDecision
  reviewerNote: string
  reviewerIdentity: string | null
}

export function createReviewDecision(
  sourceOutputRef: SourceOutputRef,
  input: DecisionInput,
  reviewedAt: string = new Date().toISOString(),
): StructuringReviewDecision {
  return {
    source_output_ref: sourceOutputRef,
    target_type: input.targetType,
    target_id: input.targetId,
    unit_id: input.unitId,
    reviewer_decision: input.reviewerDecision,
    reviewer_note: input.reviewerNote,
    reviewed_at: reviewedAt,
    reviewer_identity: input.reviewerIdentity,
  }
}

export interface CurationInput {
  noteType: CurationNoteType
  targetType?: ReviewTargetType
  targetId?: string
  unitId: string | null
  note: string
  reviewerIdentity: string | null
}

export function createCurationRecord(
  sourceOutputRef: SourceOutputRef,
  input: CurationInput,
  curationId: string,
  createdAt: string = new Date().toISOString(),
): AssetCurationRecord {
  return {
    source_output_ref: sourceOutputRef,
    curation_id: curationId,
    note_type: input.noteType,
    target_type: input.targetType,
    target_id: input.targetId,
    unit_id: input.unitId,
    note: input.note,
    created_at: createdAt,
    review_status: 'needs_review',
    reviewer_identity: input.reviewerIdentity,
  }
}

function applyPatch(
  output: StructuringPipelineOutput,
  patch: StructuringReviewPatch,
): void {
  if (!patch.unit_id || !patch.field_path.startsWith('semantic_draft.')) return

  const unit = output.units.find((candidate) => candidate.unit_id === patch.unit_id)
  if (!unit) return

  const semanticField = patch.field_path.replace(/^semantic_draft\./, '')
  if (semanticField in unit.semantic_draft) {
    ;(unit.semantic_draft as Record<string, unknown>)[semanticField] = patch.new_value
  }
}

export function createIntegratedStructuringReviewPackage(
  session: SessionState,
  exportedAt: string = new Date().toISOString(),
): IntegratedStructuringReviewPackage {
  const reviewPatches = Array.from(session.patchMap.values())
  const baseOutput = structuredClone(session.sourceOutput)
  const mergedOutput = structuredClone(session.sourceOutput)
  for (const patch of reviewPatches) {
    applyPatch(mergedOutput, patch)
  }

  return {
    package_version: 'v1',
    package_id: `pkg-${session.sourceOutputRef.document_id}-${Date.parse(exportedAt) || Date.now()}`,
    source_output_ref: session.sourceOutputRef,
    input_kind: session.inputKind,
    source_markdown: session.sourceMarkdown,
    base_output: baseOutput,
    review_patches: reviewPatches,
    review_decisions: session.decisions,
    curation_records: session.curationRecords,
    merged_output: mergedOutput,
    validation_report: {
      status: 'needs_review',
      errors: [],
      warnings: [
        'Integrated package is review material only and is not a runtime-safe reviewed asset.',
      ],
    },
    package_status: 'needs_review',
    exported_at: exportedAt,
  }
}

export function exportToJsonFile(data: unknown, filename: string): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json',
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
