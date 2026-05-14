import { z } from 'zod'

// Enums
export const DocumentStatus = z.enum([
  'official',
  'draft_for_comment',
  'deprecated',
  'unknown',
])

export const ParseStatus = z.enum([
  'parsed',
  'partial',
  'needs_review',
  'failed',
])

export const ReviewStatus = z.enum([
  'needs_review',
  'approved',
  'rejected',
  'superseded',
])

export const DocumentSourceType = z.enum([
  'external_regulation',
  'internal_policy',
  'unknown',
])

export const IssuerType = z.enum([
  'government_regulator',
  'self_regulatory_organization',
  'internal_org',
  'external_other',
  'joint_issuers',
  'unknown',
])

export const SourceLocationKind = z.enum([
  'page_number',
  'line_number',
  'paragraph_index',
  'heading_path',
  'unknown',
])

export const ValidationSeverity = z.enum([
  'info',
  'warning',
  'error',
])

export const ExtractionMethod = z.enum([
  'deterministic',
  'llm_assisted',
  'mixed',
])

export const RelationKind = z.enum([
  'definition_applies',
  'exception_to',
  'condition_for',
  'procedure_for',
  'cross_reference',
  'other_dependency',
])

export const SemanticUnitType = z.enum([
  'definition',
  'obligation',
  'prohibition',
  'procedure',
  'exception',
  'condition',
  'reporting',
  'threshold',
  'authorization',
  'liability',
  'general',
  'unknown',
])

// Sub-models
export const FileInput = z.object({
  source_id: z.string().min(1),
  source_file: z.string().min(1),
  file_type: z.enum(['pdf', 'docx', 'markdown', 'text']),
  file_ref: z.string(),
})

export const ExtractedTextBundle = z.object({
  source_id: z.string().min(1),
  source_file: z.string().min(1),
  text: z.string().min(1),
  extraction_method: ExtractionMethod,
  warnings: z.array(z.string()).default([]),
})

export const NormalizedTextInput = z.object({
  source_id: z.string().min(1),
  source_file: z.string().min(1),
  content_type: z.enum(['normalized_text', 'markdown']),
  text: z.string().min(1),
  source_type: DocumentSourceType.default('unknown'),
  metadata: z.record(z.any()).default({}),
})

export const DocumentCategory = z.object({
  category_scheme: z.enum([
    'external_regulation_type',
    'internal_policy_type',
    'business_domain',
    'compliance_topic',
    'custom',
  ]).default('custom'),
  category_code: z.string().nullable().default(null),
  category_label: z.string().nullable().default(null),
  tags: z.array(z.string()).default([]),
  evidence_text: z.string().nullable().default(null),
  confidence: z.number().min(0).max(1).nullable().default(null),
  ambiguity_notes: z.array(z.string()).default([]),
})

export const DocumentClassificationDraft = z.object({
  source_type: DocumentSourceType.default('unknown'),
  issuer_type: IssuerType.default('unknown'),
  issuer_name: z.string().nullable().default(null),
  categories: z.array(DocumentCategory).default([]),
  topic_tags: z.array(z.string()).default([]),
  classification_tags: z.array(z.string()).default([]),
  evidence_text: z.array(z.string()).default([]),
  confidence: z.number().min(0).max(1).nullable().default(null),
  review_status: ReviewStatus.default('needs_review'),
  ambiguity_notes: z.array(z.string()).default([]),
})

export const SourceLocation = z.object({
  kind: SourceLocationKind.default('unknown'),
  value: z.string().nullable().default(null),
  confidence: z.number().min(0).max(1).nullable().default(null),
})

export const TemporalMetadata = z.object({
  version_label: z.string().nullable().default(null),
  effective_date_text: z.string().nullable().default(null),
  promulgation_date_text: z.string().nullable().default(null),
  repeal_date_text: z.string().nullable().default(null),
  amendment_history_text: z.string().nullable().default(null),
  validity_notes: z.array(z.string()).default([]),
  temporal_confidence: z.number().min(0).max(1).nullable().default(null),
  ambiguity_notes: z.array(z.string()).default([]),
})

export const ExtractionProvenance = z.object({
  extraction_method: ExtractionMethod,
  prompt_contract_version: z.string().nullable().default(null),
  model_trace_id: z.string().nullable().default(null),
})

export const RegulationDocumentDraft = z.object({
  document_id: z.string().min(1),
  source_id: z.string().min(1),
  source_file: z.string().min(1),
  classification: DocumentClassificationDraft,
  title: z.string().nullable().default(null),
  document_number: z.string().nullable().default(null),
  document_status: DocumentStatus.default('unknown'),
  effective_date: z.string().nullable().default(null),
  promulgation_date: z.string().nullable().default(null),
  repeal_date: z.string().nullable().default(null),
  temporal_metadata: TemporalMetadata,
  parse_status: ParseStatus.default('needs_review'),
  warnings: z.array(z.string()).default([]),
  review_status: ReviewStatus.default('needs_review'),
})

export const HierarchyPath = z.object({
  part: z.string().nullable().default(null),
  chapter: z.string().nullable().default(null),
  section: z.string().nullable().default(null),
  article_number: z.string().nullable().default(null),
  article_title: z.string().nullable().default(null),
  paragraph_number: z.string().nullable().default(null),
  paragraph_index: z.number().nullable().default(null),
  item_number: z.string().nullable().default(null),
  item_label: z.string().nullable().default(null),
  subitem_number: z.string().nullable().default(null),
  heading_path: z.array(z.string()).default([]),
})

export const SemanticUnitDraft = z.object({
  unit_type: SemanticUnitType.default('unknown'),
  normalized_title: z.string().nullable().default(null),
  summary: z.string().nullable().default(null),
  definitions: z.array(z.string()).default([]),
  obligations: z.array(z.string()).default([]),
  exceptions: z.array(z.string()).default([]),
  applicability: z.array(z.string()).default([]),
  actors: z.array(z.string()).default([]),
  conditions: z.array(z.string()).default([]),
  trigger_events: z.array(z.string()).default([]),
  required_actions: z.array(z.string()).default([]),
  prohibited_actions: z.array(z.string()).default([]),
  deadlines: z.array(z.string()).default([]),
  thresholds: z.array(z.string()).default([]),
  subject_scope: z.array(z.string()).default([]),
  object_scope: z.array(z.string()).default([]),
  reporting_obligations: z.array(z.string()).default([]),
  evidence_text: z.array(z.string()).default([]),
  confidence: z.number().min(0).max(1).nullable().default(null),
  review_status: ReviewStatus.default('needs_review'),
  ambiguity_notes: z.array(z.string()).default([]),
})

export const RegulationUnitDraft = z.object({
  unit_id: z.string().min(1),
  document_id: z.string().min(1),
  parent_unit_id: z.string().nullable().default(null),
  order_index: z.number().int().min(0),
  unit_level: z.number().int().nullable().default(null),
  unit_kind: z.enum([
    'part',
    'chapter',
    'section',
    'article',
    'paragraph',
    'item',
    'subitem',
    'appendix',
    'unknown',
  ]).default('unknown'),
  display_label: z.string().nullable().default(null),
  source_id: z.string().min(1),
  source_file: z.string().min(1),
  source_location: SourceLocation,
  hierarchy: HierarchyPath,
  original_text: z.string().min(1).refine((v) => v.trim().length > 0, {
    message: 'original_text must not be empty',
  }),
  normalized_text: z.string().nullable().default(null),
  semantic_draft: SemanticUnitDraft,
  review_status: ReviewStatus.default('needs_review'),
  warnings: z.array(z.string()).default([]),
})

export const ReferenceCandidate = z.object({
  candidate_id: z.string().min(1),
  document_id: z.string().min(1),
  from_unit_id: z.string().min(1),
  target_label: z.string().min(1),
  evidence_text: z.string().min(1),
  source_location: SourceLocation.nullable().default(null),
  confidence: z.number().min(0).max(1).nullable().default(null),
  ambiguity_notes: z.array(z.string()).default([]),
  warnings: z.array(z.string()).default([]),
})

export const DependencyEdgeDraft = z.object({
  edge_id: z.string().min(1),
  document_id: z.string().min(1),
  from_unit_id: z.string().min(1),
  to_unit_id: z.string().nullable().default(null),
  target_document_id: z.string().nullable().default(null),
  target_document_title: z.string().nullable().default(null),
  target_source_type: DocumentSourceType.nullable().default(null),
  target_label: z.string().nullable().default(null),
  target_scope: z.enum(['same_document', 'external_document', 'unknown']),
  resolution_status: z.enum(['resolved', 'unresolved', 'ambiguous']),
  relation_kind: RelationKind,
  source_candidate_ids: z.array(z.string()).default([]),
  evidence_text: z.string().min(1),
  confidence: z.number().min(0).max(1).nullable().default(null),
  ambiguity_notes: z.array(z.string()).default([]),
  review_status: ReviewStatus.default('needs_review'),
})

export const ResolvedDependencyGraphDraft = z.object({
  graph_id: z.string().min(1),
  document_id: z.string().min(1),
  reference_candidate_ids: z.array(z.string()).default([]),
  dependency_edges: z.array(DependencyEdgeDraft).default([]),
  warnings: z.array(z.string()).default([]),
})

export const StructuringValidationFinding = z.object({
  stage: z.enum([
    'input',
    'document',
    'unit',
    'semantic',
    'reference',
    'dependency',
    'output',
  ]).default('output'),
  target_type: z.enum([
    'document',
    'unit',
    'semantic_draft',
    'reference_candidate',
    'dependency_edge',
    'pipeline_output',
    'unknown',
  ]).default('unknown'),
  target_id: z.string().nullable().default(null),
  code: z.string().min(1),
  severity: ValidationSeverity,
  message: z.string().min(1),
  document_id: z.string().nullable().default(null),
  unit_id: z.string().nullable().default(null),
  source_location: SourceLocation.nullable().default(null),
})

export const StructuringValidationReport = z.object({
  document_id: z.string().min(1),
  summary: z.string().min(1),
  findings: z.array(StructuringValidationFinding).default([]),
  error_count: z.number().int().default(0),
  warning_count: z.number().int().default(0),
  info_count: z.number().int().default(0),
  has_errors: z.boolean().default(false),
})

export const StructuringPipelineOutput = z.object({
  contract_version: z.string().min(1).default('v1'),
  extraction_provenance: ExtractionProvenance,
  document: RegulationDocumentDraft,
  units: z.array(RegulationUnitDraft).default([]),
  reference_candidates: z.array(ReferenceCandidate).default([]),
  dependency_graph: ResolvedDependencyGraphDraft,
  validation_report: StructuringValidationReport,
})

// Types
export type DocumentStatus = z.infer<typeof DocumentStatus>
export type ParseStatus = z.infer<typeof ParseStatus>
export type ReviewStatus = z.infer<typeof ReviewStatus>
export type DocumentSourceType = z.infer<typeof DocumentSourceType>
export type IssuerType = z.infer<typeof IssuerType>
export type SourceLocationKind = z.infer<typeof SourceLocationKind>
export type ValidationSeverity = z.infer<typeof ValidationSeverity>
export type ExtractionMethod = z.infer<typeof ExtractionMethod>
export type RelationKind = z.infer<typeof RelationKind>
export type SemanticUnitType = z.infer<typeof SemanticUnitType>

export type FileInput = z.infer<typeof FileInput>
export type ExtractedTextBundle = z.infer<typeof ExtractedTextBundle>
export type NormalizedTextInput = z.infer<typeof NormalizedTextInput>
export type DocumentCategory = z.infer<typeof DocumentCategory>
export type DocumentClassificationDraft = z.infer<typeof DocumentClassificationDraft>
export type SourceLocation = z.infer<typeof SourceLocation>
export type TemporalMetadata = z.infer<typeof TemporalMetadata>
export type ExtractionProvenance = z.infer<typeof ExtractionProvenance>
export type RegulationDocumentDraft = z.infer<typeof RegulationDocumentDraft>
export type HierarchyPath = z.infer<typeof HierarchyPath>
export type SemanticUnitDraft = z.infer<typeof SemanticUnitDraft>
export type RegulationUnitDraft = z.infer<typeof RegulationUnitDraft>
export type ReferenceCandidate = z.infer<typeof ReferenceCandidate>
export type DependencyEdgeDraft = z.infer<typeof DependencyEdgeDraft>
export type ResolvedDependencyGraphDraft = z.infer<typeof ResolvedDependencyGraphDraft>
export type StructuringValidationFinding = z.infer<typeof StructuringValidationFinding>
export type StructuringValidationReport = z.infer<typeof StructuringValidationReport>
export type StructuringPipelineOutput = z.infer<typeof StructuringPipelineOutput>
