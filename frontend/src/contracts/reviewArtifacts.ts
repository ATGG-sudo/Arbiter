import { z } from 'zod'
import { StructuringPipelineOutput } from './structuringOutput'

export const ReviewDecision = z.enum([
  'approved',
  'rejected',
  'needs_changes',
  'needs_more_evidence',
  'superseded',
])

export const ReviewTargetType = z.enum([
  'document',
  'unit',
  'semantic_draft',
  'reference_candidate',
  'dependency_edge',
  'curation_note',
])

export const CurationNoteType = z.enum([
  'expert_note',
  'candidate_rule_hint',
  'scenario_example',
  'ambiguity_case',
  'dependency_issue',
])

export const WorkbenchInputKind = z.enum([
  'markdown',
  'structuring_output_json',
])

export const IntegratedPackageStatus = z.enum([
  'needs_review',
  'reviewed_for_structuring',
])

export const SourceOutputRef = z.object({
  contract_version: z.string().min(1),
  document_id: z.string().min(1),
  source_id: z.string().min(1),
  source_file: z.string().min(1),
  loaded_at: z.string().min(1),
})

export const StructuringReviewPatch = z.object({
  source_output_ref: SourceOutputRef,
  target_type: ReviewTargetType,
  target_id: z.string().min(1),
  unit_id: z.string().nullable().default(null),
  field_path: z.string().min(1),
  old_value: z.any(),
  new_value: z.any(),
  reviewer_note: z.string().default(''),
  reviewer_decision: ReviewDecision,
  reviewed_at: z.string().min(1),
  reviewer_identity: z.string().nullable().default(null),
})

export const StructuringReviewDecision = z.object({
  source_output_ref: SourceOutputRef,
  target_type: ReviewTargetType,
  target_id: z.string().min(1),
  unit_id: z.string().nullable().default(null),
  reviewer_decision: ReviewDecision,
  reviewer_note: z.string().default(''),
  reviewed_at: z.string().min(1),
  reviewer_identity: z.string().nullable().default(null),
})

export const AssetCurationRecord = z.object({
  source_output_ref: SourceOutputRef,
  curation_id: z.string().min(1),
  note_type: CurationNoteType,
  target_type: ReviewTargetType.optional(),
  target_id: z.string().optional(),
  unit_id: z.string().nullable().default(null),
  note: z.string().min(1),
  created_at: z.string().min(1),
  review_status: z.string().min(1).default('needs_review'),
  reviewer_identity: z.string().nullable().default(null),
})

export const IntegratedPackageValidationReport = z.object({
  status: z.string().min(1),
  errors: z.array(z.string()).default([]),
  warnings: z.array(z.string()).default([]),
})

export const IntegratedStructuringReviewPackage = z.object({
  package_version: z.string().min(1),
  package_id: z.string().min(1),
  source_output_ref: SourceOutputRef,
  input_kind: WorkbenchInputKind,
  source_markdown: z.string().nullable().default(null),
  base_output: StructuringPipelineOutput,
  review_patches: z.array(StructuringReviewPatch).default([]),
  review_decisions: z.array(StructuringReviewDecision).default([]),
  curation_records: z.array(AssetCurationRecord).default([]),
  merged_output: StructuringPipelineOutput,
  validation_report: IntegratedPackageValidationReport,
  package_status: IntegratedPackageStatus,
  exported_at: z.string().min(1),
}).superRefine((pkg, ctx) => {
  if (pkg.input_kind === 'markdown' && !pkg.source_markdown?.trim()) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      path: ['source_markdown'],
      message: 'source_markdown is required for markdown input',
    })
  }
})

export type ReviewDecision = z.infer<typeof ReviewDecision>
export type ReviewTargetType = z.infer<typeof ReviewTargetType>
export type CurationNoteType = z.infer<typeof CurationNoteType>
export type WorkbenchInputKind = z.infer<typeof WorkbenchInputKind>
export type IntegratedPackageStatus = z.infer<typeof IntegratedPackageStatus>
export type SourceOutputRef = z.infer<typeof SourceOutputRef>
export type StructuringReviewPatch = z.infer<typeof StructuringReviewPatch>
export type StructuringReviewDecision = z.infer<typeof StructuringReviewDecision>
export type AssetCurationRecord = z.infer<typeof AssetCurationRecord>
export type IntegratedPackageValidationReport = z.infer<typeof IntegratedPackageValidationReport>
export type IntegratedStructuringReviewPackage = z.infer<typeof IntegratedStructuringReviewPackage>
