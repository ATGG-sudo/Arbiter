import { z } from 'zod'

export const RuntimeDraftStatus = z.enum([
  'draft',
  'needs_review',
  'reviewed',
])

export const RuntimeScenarioInput = z.object({
  scenario_id: z.string().min(1),
  question: z.string().min(1),
  structured_fields: z.record(z.any()).optional(),
  as_of_date: z.string().nullable().default(null),
})

export const RuntimeCitationView = z.object({
  citation_id: z.string().min(1),
  unit_id: z.string().min(1),
  document_id: z.string().min(1),
  source_version: z.string().nullable().default(null),
  article_or_clause: z.string().nullable().default(null),
  provenance: z.string().nullable().default(null),
  as_of_date: z.string().nullable().default(null),
})

export const RuntimeEvidenceView = z.object({
  evidence_id: z.string().min(1),
  unit_id: z.string().optional(),
  excerpt: z.string().optional(),
  dependency_context: z.array(z.string()).default([]),
  provenance: z.string().nullable().default(null),
  as_of_date: z.string().nullable().default(null),
})

export const RuntimeTraceStep = z.object({
  step_id: z.string().min(1),
  label: z.string().min(1),
  status: z.string().min(1),
})

export const RuntimeTraceView = z.object({
  trace_id: z.string().min(1),
  steps: z.array(RuntimeTraceStep).default([]),
  redaction_warnings: z.array(z.string()).default([]),
})

export const RuntimeJudgmentDraftView = z.object({
  draft_id: z.string().min(1),
  scenario_id: z.string().min(1),
  status: RuntimeDraftStatus,
  summary: z.string().min(1),
  confidence: z.number().nullable().default(null),
  warnings: z.array(z.string()).default([]),
  validation_status: z.string().min(1),
  human_review_required: z.boolean(),
  citations: z.array(RuntimeCitationView).default([]),
  evidence: z.array(RuntimeEvidenceView).default([]),
  trace: RuntimeTraceView.optional(),
})

export type RuntimeDraftStatus = z.infer<typeof RuntimeDraftStatus>
export type RuntimeScenarioInput = z.infer<typeof RuntimeScenarioInput>
export type RuntimeCitationView = z.infer<typeof RuntimeCitationView>
export type RuntimeEvidenceView = z.infer<typeof RuntimeEvidenceView>
export type RuntimeTraceStep = z.infer<typeof RuntimeTraceStep>
export type RuntimeTraceView = z.infer<typeof RuntimeTraceView>
export type RuntimeJudgmentDraftView = z.infer<typeof RuntimeJudgmentDraftView>
