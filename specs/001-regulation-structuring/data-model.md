# Data Model: Regulation Structuring Pipeline

## Enums

### DocumentStatus

- `official`
- `draft_for_comment`
- `deprecated`
- `unknown`

### ParseStatus

- `needs_review`
- `failed`

The default for `RegulationDocumentDraft.parse_status` is `needs_review`.

### ReviewStatus

- `needs_review`
- `approved`
- `rejected`
- `superseded`

The default for `RegulationUnitDraft.review_status` and
`DependencyEdgeDraft.review_status` is `needs_review`. `SemanticUnitDraft` and
`DocumentClassificationDraft` also use `needs_review` in this feature.
This feature's pipeline must create all reviewable outputs with
`review_status = needs_review`. `approved`, `rejected`, and `superseded` are
reserved for later review or promotion workflows and must not be assigned by
this feature.

### DocumentSourceType

- `external_regulation`
- `internal_policy`
- `unknown`

The pipeline must preserve whether a source is an external regulatory document
or an internal policy when that information is supplied or recognizable.

### IssuerType

- `government_regulator`
- `self_regulatory_organization`
- `internal_org`
- `external_other`
- `unknown`

Issuer type is intentionally coarse. Detailed issuer names and compliance topics
belong in strings, tags, and review notes rather than exhaustive enums.

### SourceLocationKind

- `page_number`
- `line_number`
- `paragraph_index`
- `heading_path`
- `unknown`

### ValidationSeverity

- `info`
- `warning`
- `error`

### ExtractionMethod

- `deterministic`
- `llm_assisted`
- `mixed`

The method records how a draft or bundle was produced. It must not expose
provider secrets, full prompts, or unnecessary raw sensitive text.

### RelationKind

- `definition_applies`
- `exception_to`
- `condition_for`
- `procedure_for`
- `cross_reference`
- `other_dependency`

All relation kinds are draft interpretations until human review. Semantic
relation kinds such as `definition_applies`, `procedure_for`, `condition_for`,
and `exception_to` are optional/future extension points unless clear textual
evidence supports them.

## Entities

### FileInput

Optional adapter input for future file-upload or file-extraction features.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_id` | string | yes | Stable caller-provided source identifier |
| `source_file` | string | yes | File name or source path label |
| `file_type` | string | yes | `pdf`, `docx`, `markdown`, or `text` |
| `file_ref` | string | yes | Opaque controlled-environment reference |

Validation rules:
- FileInput is not a direct structuring input for this first slice.
- OCR, password handling, and full layout recovery are outside this spec.
- The adapter boundary is FileInput -> ExtractedTextBundle -> NormalizedTextInput.

### ExtractedTextBundle

Optional adapter output that carries extracted text into normalization.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_id` | string | yes | Links to FileInput |
| `source_file` | string | yes | Traceable source label |
| `text` | string | yes | Extracted text or Markdown-like text |
| `extraction_method` | ExtractionMethod | yes | Usually deterministic or mixed |
| `warnings` | list[string] | yes | Extraction warnings before structuring |

Validation rules:
- `text` must not be empty before conversion to NormalizedTextInput.
- Extraction warnings are carried forward into validation findings where useful.
- ExtractedTextBundle does not preserve full layout and is not runtime input.

### NormalizedTextInput

Represents direct input to the offline structuring pipeline.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_id` | string | yes | Stable caller-provided source identifier |
| `source_file` | string | yes | File name or source path label; must not require an absolute local path |
| `content_type` | string | yes | `normalized_text` or `markdown` |
| `text` | string | yes | Extracted normalized text or Markdown content |
| `source_type` | DocumentSourceType | no | Optional source-type hint: `external_regulation`, `internal_policy`, or `unknown` |
| `metadata` | object | no | Optional caller-provided title/date/status/classification hints |

Validation rules:
- `text` must not be empty after trimming.
- `content_type` must be one of the direct input types.
- Missing `source_type` defaults to `unknown` in the output classification.
- `source_file` must be a label suitable for traceability, not a hard-coded
  environment-specific dependency.

### DocumentCategory

Extensible category/tag record for document classification.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `category_code` | string or null | no | Optional stable category code when available |
| `category_label` | string or null | no | Human-readable category label |
| `tags` | list[string] | yes | Extensible tags; not an exhaustive taxonomy |
| `evidence_text` | string or null | no | Bounded evidence supporting the category |
| `confidence` | number or null | no | Optional confidence score |
| `ambiguity_notes` | list[string] | yes | Review notes for unclear classification |

Validation rules:
- Detailed compliance topics must remain extensible through `tags` or other
  string lists, not hard-coded exhaustive enums.
- Category records are draft classification clues and do not establish reviewed
  document meaning.

### DocumentClassificationDraft

Reviewable document classification draft.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `source_type` | DocumentSourceType | yes | Distinguishes external regulations from internal policies |
| `issuer_type` | IssuerType | yes | Coarse issuer type |
| `issuer_name` | string or null | no | Issuer name when available |
| `categories` | list[DocumentCategory] | yes | Extensible document categories and tags |
| `topic_tags` | list[string] | yes | Extensible compliance-topic tags |
| `classification_tags` | list[string] | yes | Other draft classification tags |
| `evidence_text` | list[string] | yes | Bounded evidence excerpts |
| `confidence` | number or null | no | Optional confidence score |
| `review_status` | ReviewStatus | yes | Defaults to `needs_review` |
| `ambiguity_notes` | list[string] | yes | Review notes for unclear classification |

Validation rules:
- `review_status` must default to `needs_review`.
- Missing or uncertain values default to `unknown`, null, or empty lists.
- LLM-assisted classification extraction must validate against this schema
  before inclusion.
- Classifications remain draft / needs_review unless confirmed by a later
  review workflow.
- Classification tags must not imply a final legal interpretation or active
  runtime rule status.

### SourceLocation

Represents the best available source location for a unit.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `kind` | SourceLocationKind | yes | May be page, line, paragraph, heading path, or unknown |
| `value` | string | no | Human-readable location value |
| `confidence` | string | no | Optional confidence label such as `explicit`, `derived`, or `unknown` |

Validation rules:
- `kind = unknown` may omit `value`.
- Known location kinds are expected to include a value; absence is reported as
  a validation finding.

### TemporalMetadata

Reviewable version and validity context for a document.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `version_label` | string or null | no | Source version, amendment label, or release label when available |
| `amendment_history_text` | string or null | no | Bounded source text describing amendments when available |
| `validity_notes` | list[string] | yes | Validity or temporal review notes |
| `temporal_confidence` | number or null | no | Optional confidence score |
| `ambiguity_notes` | list[string] | yes | Notes for missing or unclear temporal facts |

Validation rules:
- Missing or uncertain values remain null or empty lists.
- Temporal facts must not be fabricated from weak hints.
- Contradictory effective, repeal, version, or amendment facts are reported in
  StructuringValidationReport.

### ExtractionProvenance

Bounded provenance for draft extraction.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `extraction_method` | ExtractionMethod | yes | deterministic, llm_assisted, or mixed |
| `prompt_contract_version` | string or null | no | Prompt/output contract version when LLM-assisted extraction was used |
| `model_trace_id` | string or null | no | Bounded trace identifier when a model call was used |

Validation rules:
- Deterministic-only output may leave prompt/model fields null.
- LLM-assisted or mixed output should include a prompt contract version and
  model trace ID when available.
- Provenance must not contain secrets, full prompts, API payloads, or
  unnecessary raw sensitive text.

### RegulationDocumentDraft

Document-level draft metadata for the submitted regulation or policy.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `document_id` | string | yes | Stable draft document identifier |
| `source_id` | string | yes | Links back to `NormalizedTextInput.source_id` |
| `source_file` | string | yes | Traceable source file label |
| `classification` | DocumentClassificationDraft | yes | Draft classification for source type, issuer, category, and tags |
| `title` | string or null | yes | Unknown when absent |
| `document_status` | DocumentStatus | yes | Defaults to `unknown` when not recognizable |
| `effective_date` | date or null | yes | Null when unknown |
| `promulgation_date` | date or null | yes | Null when unknown |
| `repeal_date` | date or null | yes | Null when unknown |
| `temporal_metadata` | TemporalMetadata | yes | Version, amendment, validity, and ambiguity context |
| `parse_status` | ParseStatus | yes | Defaults to `needs_review` |
| `warnings` | list[string] | yes | Document-level warning codes or messages |

Validation rules:
- `parse_status` must default to `needs_review`.
- `classification.review_status` must default to `needs_review`.
- Missing dates must be represented as unknown/null, not fabricated.
- Missing version or amendment facts remain null or notes, not guesses.
- Document status must be one of the allowed values.

### HierarchyPath

Structured path for a unit inside the document.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `chapter` | string or null | no | Chapter label/title when present |
| `section` | string or null | no | Section label/title when present |
| `article_number` | string or null | no | Article number when present |
| `article_title` | string or null | no | Article title when present |
| `paragraph_index` | integer or null | no | Paragraph order inside article |
| `item_label` | string or null | no | Item marker when present |

Validation rules:
- Values are preserved as document labels where practical.
- Missing levels remain null rather than guessed.

### SemanticUnitDraft

Schema-constrained semantic draft fields for a regulation unit.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `unit_type` | string or null | no | Draft semantic type such as definition, obligation, exception, condition, procedure, or other |
| `normalized_title` | string or null | no | Normalized title when language understanding is needed |
| `definitions` | list[string] | yes | Draft definitions detected in the unit |
| `obligations` | list[string] | yes | Draft obligations detected in the unit |
| `exceptions` | list[string] | yes | Draft exceptions detected in the unit |
| `applicability` | list[string] | yes | Draft applicability clues |
| `actors` | list[string] | yes | Draft actors or subjects |
| `conditions` | list[string] | yes | Draft conditions |
| `trigger_events` | list[string] | yes | Draft event conditions that may trigger the unit |
| `required_actions` | list[string] | yes | Draft required actions |
| `prohibited_actions` | list[string] | yes | Draft prohibited actions |
| `deadlines` | list[string] | yes | Draft deadline or timing clues |
| `thresholds` | list[string] | yes | Draft numeric or qualitative threshold clues |
| `subject_scope` | list[string] | yes | Draft subject scope |
| `object_scope` | list[string] | yes | Draft object or transaction scope |
| `reporting_obligations` | list[string] | yes | Draft reporting or disclosure obligations |
| `evidence_text` | list[string] | yes | Bounded evidence excerpts supporting extracted fields |
| `confidence` | number or null | no | Optional confidence score |
| `review_status` | ReviewStatus | yes | Defaults to `needs_review` |
| `ambiguity_notes` | list[string] | yes | Notes requiring human review |

Validation rules:
- `review_status` must default to `needs_review`.
- LLM-assisted semantic extraction must validate against this schema before
  inclusion.
- Semantic fields may be initialized with null scalar values, empty lists, and
  ambiguity notes when extraction cannot produce a validated result.
- Free-form prose is not accepted as the primary output.
- Semantic fields remain draft-only and reviewable.
- Populated semantic fields must be evidence-backed where applicable.

### RegulationUnitDraft

Reviewable structured unit extracted from the source document.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `unit_id` | string | yes | Stable draft unit identifier |
| `document_id` | string | yes | Parent document draft |
| `parent_unit_id` | string or null | yes | Parent unit for explicit tree navigation; null for roots |
| `order_index` | integer | yes | Stable order among sibling units |
| `display_label` | string or null | no | Review UI label when available |
| `source_id` | string | yes | Original source input |
| `source_file` | string | yes | Traceable source file label |
| `source_location` | SourceLocation | yes | Best available source location |
| `hierarchy` | HierarchyPath | yes | Chapter/section/article/paragraph/item path |
| `original_text` | string | yes | Preserved source text for this unit |
| `normalized_text` | string | no | Cleaned text for downstream review/search |
| `semantic_draft` | SemanticUnitDraft | yes | Schema-constrained semantic draft fields |
| `review_status` | ReviewStatus | yes | Defaults to `needs_review` |
| `warnings` | list[string] | yes | Unit-level warning codes or messages |

Validation rules:
- `original_text` must not be empty.
- `review_status` must default to `needs_review`.
- Unit IDs must be unique within a pipeline output.
- `parent_unit_id` must reference an existing unit or be null.
- `order_index` must be stable and non-negative within a sibling group.
- HierarchyPath preserves source document labels; `parent_unit_id` and
  `order_index` support explicit tree navigation and stable review UI rendering.

### ReferenceCandidate

Textual reference clue detected before dependency resolution.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `candidate_id` | string | yes | Stable draft candidate identifier |
| `document_id` | string | yes | Parent document draft |
| `from_unit_id` | string | yes | Unit containing the reference clue |
| `target_label` | string | yes | Referenced article/section/term label as text |
| `evidence_text` | string | yes | Bounded excerpt containing the clue |
| `source_location` | SourceLocation | no | Location when available |
| `confidence` | number or null | no | Optional confidence score |
| `ambiguity_notes` | list[string] | yes | Review notes for unclear references |
| `warnings` | list[string] | yes | Ambiguity or missing-target warnings |

Validation rules:
- A candidate is not a resolved dependency edge.
- Evidence text must be bounded and traceable.
- LLM-assisted candidate extraction must validate against this schema before
  inclusion.

### DependencyEdgeDraft / RegulationUnitRelationDraft

Proposed resolved dependency edge between units.

RegulationUnitRelationDraft is a compatibility alias for the same proposed edge
schema as DependencyEdgeDraft in this feature.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `edge_id` | string | yes | Stable draft edge identifier |
| `document_id` | string | yes | Parent document draft |
| `from_unit_id` | string | yes | Source unit |
| `to_unit_id` | string or null | no | Proposed target unit when resolved |
| `target_document_id` | string or null | no | Proposed target document when the edge points outside the current document |
| `target_document_title` | string or null | no | Proposed target document title when available |
| `target_source_type` | DocumentSourceType or null | no | Target document source type when available |
| `target_label` | string or null | no | Referenced target label when unresolved or external |
| `target_scope` | string | yes | `same_document`, `external_document`, or `unknown` |
| `resolution_status` | string | yes | `resolved`, `unresolved`, or `ambiguous` |
| `relation_kind` | RelationKind | yes | Draft dependency type |
| `source_candidate_ids` | list[string] | yes | Reference candidates supporting the edge |
| `evidence_text` | string | yes | Bounded evidence excerpt |
| `confidence` | number or null | no | Optional confidence score |
| `ambiguity_notes` | list[string] | yes | Review notes for uncertainty |
| `review_status` | ReviewStatus | yes | Defaults to `needs_review` |

Validation rules:
- Proposed edges remain draft / needs_review unless approved by a later review
  workflow.
- `to_unit_id` is required only when `resolution_status = resolved` and
  `target_scope = same_document`.
- `target_document_id` may be set when a proposed edge targets a known external
  document; unresolved external references may leave it null.
- Cross-document links between internal policies and external regulations should
  preserve `target_document_id`, `target_document_title`, and
  `target_source_type` when available.
- Unresolved or ambiguous references must preserve `target_label` when known.
- Edges must not claim final legal meaning.
- Edges must provide evidence, confidence when available, and ambiguity notes.
- ReviewedDependencyEdge is a downstream human-approved artifact and is not
  produced by this feature.

### ResolvedDependencyGraphDraft

Reviewable dependency graph draft for a structured document.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `graph_id` | string | yes | Stable graph draft identifier |
| `document_id` | string | yes | Parent document draft |
| `reference_candidate_ids` | list[string] | yes | IDs of top-level textual reference clues included in this graph |
| `dependency_edges` | list[DependencyEdgeDraft] | yes | Proposed resolved edges |
| `warnings` | list[string] | yes | Graph-level warning codes or messages |

Validation rules:
- Reference candidates and resolved edges must remain separate.
- Full ReferenceCandidate records live at the pipeline output top level; graph
  records reference them by ID to avoid duplication.
- Circular references, ambiguous edges, and unresolved references are reported
  in the validation report.

### StructuringValidationFinding

One structured warning or error.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `code` | string | yes | Stable machine-readable finding code |
| `severity` | ValidationSeverity | yes | info/warning/error |
| `message` | string | yes | Human-readable summary |
| `document_id` | string | no | Related document when available |
| `unit_id` | string | no | Related unit when available |
| `source_location` | SourceLocation | no | Location when available |

### StructuringValidationReport

Structured report for parser confidence and review needs.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `document_id` | string | yes | Parent document draft |
| `summary` | string | yes | Bounded review summary |
| `findings` | list[StructuringValidationFinding] | yes | All warnings/errors |
| `has_errors` | boolean | yes | True when any error-level finding exists |

Validation rules:
- Duplicate IDs, malformed hierarchy, missing source provenance,
  LLM schema validation failures, temporal ambiguity, missing extraction
  provenance, invalid tree links, unresolved references, ambiguous dependency
  edges, classification ambiguity, semantic draft gaps, and circular references
  must be reported as findings.

### StructuringPipelineOutput

Complete output bundle.

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `contract_version` | string | yes | Starts at `v1` |
| `extraction_provenance` | ExtractionProvenance | yes | Bounded bundle-level extraction metadata |
| `document` | RegulationDocumentDraft | yes | Document-level draft |
| `units` | list[RegulationUnitDraft] | yes | Extracted units with semantic draft fields |
| `reference_candidates` | list[ReferenceCandidate] | yes | Textual reference clues |
| `dependency_graph` | ResolvedDependencyGraphDraft | yes | Reviewable graph draft |
| `validation_report` | StructuringValidationReport | yes | Warnings/errors |

Validation rules:
- Output must serialize to JSON and parse back without data loss.
- LLM-assisted outputs must validate against the relevant draft schemas before
  inclusion.
- Output must not contain JudgmentResult, active RulePack, formal RuleItem,
  final legal judgment, or runtime agent answer.
- Every unit, candidate, and edge must reference the document draft.
- StructuringPipelineOutput is not runtime-safe. A later review/promotion
  workflow must convert approved drafts into reviewed runtime assets.
