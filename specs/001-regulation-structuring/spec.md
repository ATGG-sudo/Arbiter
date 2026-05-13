# Feature Specification: Regulation Structuring Pipeline

**Feature Branch**: `001-regulation-structuring`
**Created**: 2026-05-12
**Status**: Draft
**Input**: User description: "Regulation Structuring Pipeline"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Structured Draft (Priority: P1)

As a compliance reviewer, I can submit a regulation or internal policy document
and receive a structured draft that is ready for manual review.

**Why this priority**: The system cannot support reliable retrieval or later
judgment workflows unless raw documents first become traceable draft assets.

**Independent Test**: Submit a document with recognizable hierarchy and verify
that the result contains a RegulationDocumentDraft, a RegulationUnitDraft list,
and a validation report without producing any judgment or formal rule output.

**Acceptance Scenarios**:

1. **Given** a readable regulation document with chapters and articles, **When**
   the reviewer submits it for structuring, **Then** the system returns a draft
   document record and structured units preserving hierarchy and original text.
2. **Given** a readable policy document with no formal article numbers, **When**
   the reviewer submits it for structuring, **Then** the system still returns
   reviewable units and reports the missing or weak hierarchy as warnings.

---

### User Story 2 - Inspect Traceable Units (Priority: P2)

As a compliance reviewer, I can inspect each parsed unit with its source,
hierarchy, explicit tree position, document status, dates, document parse
status, and unit review status.

**Why this priority**: Human review depends on knowing where each unit came from
and whether the parser inferred, missed, or preserved important document facts.

**Independent Test**: Open the structured output for a submitted document and
verify that every unit exposes document identity, source file, source location
when available, original text, hierarchy, parent/order/display metadata, status
context, and unit review status.

**Acceptance Scenarios**:

1. **Given** a structured draft with multiple articles, **When** the reviewer
   selects any unit, **Then** the reviewer can trace it back to the source
   document and inspect the preserved original text.
2. **Given** a document that states effective, promulgation, or repeal dates,
   **When** the draft is generated, **Then** those dates are captured when
   recognizable and otherwise explicitly marked unknown with temporal ambiguity
   notes or validation findings.

---

### User Story 3 - Review Warnings (Priority: P3)

As a compliance reviewer, I can see parsing warnings and decide what requires
manual review before any asset can be promoted for runtime use.

**Why this priority**: Suspicious parsing must be visible instead of silently
becoming evidence for later compliance workflows.

**Independent Test**: Submit inputs with duplicated article numbers, missing
titles, conflicting dates, or unclear cross-references and verify that the
validation report lists those issues for review.

**Acceptance Scenarios**:

1. **Given** a document with duplicated article numbers, **When** structuring
   completes, **Then** the validation report flags the duplicate instead of
   accepting it silently.
2. **Given** a document with ambiguous references, **When** structuring
   completes, **Then** textual reference clues are recorded as candidates and
   any proposed resolved dependency edges remain draft / needs_review.

---

### User Story 4 - Preserve Runtime Boundary (Priority: P4)

As a runtime developer, I can rely on reviewed structured assets instead of
exposing raw documents or the structuring pipeline to the judgment agent.

**Why this priority**: The Agent Runtime must not perform raw document parsing
or treat draft assets as formal judgment evidence.

**Independent Test**: Verify that the pipeline output contains only draft
regulation assets and validation data, and that no judgment agent action can
invoke the structuring pipeline directly.

**Acceptance Scenarios**:

1. **Given** a generated draft, **When** the output is inspected, **Then** it
   does not contain JudgmentResult, formal RuleItem, or active RulePack records.
2. **Given** the ComplianceJudgmentAgent runtime surface, **When** available
   runtime actions are inspected, **Then** the structuring pipeline is not
   available as a judgment tool.

### Edge Cases

- Direct normalized text or Markdown input is empty, unsupported, or contains no
  extractable text. Unreadable, password-protected, or unsupported PDF/Word
  source files are handled by future file-intake adapters before this
  structuring feature receives text.
- Source hierarchy is partial, malformed, or uses mixed numbering styles.
- Source hierarchy contains nested units that need explicit parent/order data for
  later review UI navigation.
- Article numbers are duplicated, skipped, or nested inconsistently.
- Article title, version label, effective date, promulgation date, repeal date,
  amendment history, validity notes, or document status is absent or
  contradictory.
- Cross-references are present but ambiguous, incomplete, or refer to units not
  found in the same document.
- Multiple source locations could map to the same extracted unit.
- Input contains sensitive raw text that should not be repeated unnecessarily
  in logs or trace summaries.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow an admin or compliance reviewer to submit
  normalized text or Markdown extracted from an external regulation or internal
  policy document for offline structuring.
- **FR-002**: The system MUST accept normalized text and Markdown as direct
  inputs, and MUST define a minimal optional intake adapter boundary of
  FileInput -> ExtractedTextBundle -> NormalizedTextInput for future file-upload
  and extraction workflows. PDF and Word are not direct first-slice structuring
  inputs.
- **FR-003**: The system MUST produce a RegulationDocumentDraft describing the
  source document identity, source file, document classification draft,
  document title when available, document status, relevant dates, and
  parse_status.
- **FR-004**: The system MUST classify document status as one of official,
  draft_for_comment, deprecated, or unknown.
- **FR-005**: RegulationDocumentDraft MUST include a
  DocumentClassificationDraft with DocumentSourceType, DocumentCategory,
  IssuerType, extensible tags, and review_status = needs_review.
- **FR-006**: The classification model MUST distinguish external regulations
  from internal policies, while detailed compliance topics remain extensible
  through lists/tags rather than hard-coded exhaustive enums.
- **FR-007**: The system MUST capture effective date, promulgation date, and
  repeal date when recognizable, and MUST include temporal metadata for
  version_label, amendment_history_text, validity_notes, temporal_confidence,
  and ambiguity_notes where available. Missing or uncertain temporal information
  MUST remain null/unknown with validation findings or ambiguity notes, not be
  fabricated.
- **FR-008**: The system MUST produce a RegulationUnitDraft list for structured
  units detected in the source document.
- **FR-009**: Each RegulationUnitDraft MUST preserve source traceability,
  including document identity, source file, source location when available, and
  original text.
- **FR-010**: Source location MAY be page number, line number, paragraph index,
  heading path, or unknown depending on the source format.
- **FR-011**: Each generated unit MUST include hierarchy information for common
  levels such as chapter, section, article, paragraph, and item when present or
  proposed by validated LLM-assisted extraction.
- **FR-012**: Article number and article title MUST be captured when present or
  proposed with evidence by validated LLM-assisted extraction.
- **FR-013**: Each RegulationDocumentDraft MUST default to
  parse_status = needs_review.
- **FR-014**: ReviewStatus MUST support needs_review, approved, rejected, and
  superseded for downstream review lifecycle compatibility, but this feature's
  pipeline MUST create all reviewable outputs with review_status = needs_review.
  Other statuses are reserved for later review or promotion workflows and MUST
  NOT be assigned by this feature.
- **FR-015**: The system MUST produce ReferenceCandidate records when textual
  cross-reference clues are detected.
- **FR-016**: ReferenceCandidate records MUST remain textual clues and MUST stay
  distinct from proposed DependencyEdgeDraft / RegulationUnitRelationDraft
  records. A later human review workflow may approve downstream
  ReviewedDependencyEdge records, but this feature does not produce them.
- **FR-017**: The system MAY propose DependencyEdgeDraft /
  RegulationUnitRelationDraft records between units when a dependency can be
  resolved from available evidence, including cross-document draft targets when
  enough source evidence is available. In this feature,
  RegulationUnitRelationDraft is a compatibility alias for the same draft edge
  schema as DependencyEdgeDraft.
- **FR-018**: DependencyEdgeDraft MUST preserve `target_document_id`,
  `target_document_title`, and `target_source_type` when available for
  cross-document links between internal policies and external regulations.
- **FR-019**: Proposed dependency edges MUST include evidence, confidence, and
  ambiguity notes when available, and MUST remain draft / needs_review until
  approved by a later human review workflow. All relation kinds remain draft
  interpretations, and no dependency edge is a final legal interpretation.
- **FR-020**: The system MUST produce a ResolvedDependencyGraphDraft that keeps
  reference candidate IDs separate from proposed dependency edges.
- **FR-021**: The system MUST use a hybrid extraction strategy: deterministic
  code handles intake, source preservation, obvious structural hints, stable
  source_id / document_id linkage, JSON serialization, schema validation, and
  validation reports; LLM-assisted
  extraction handles variable-format hierarchy interpretation, semantic unit
  extraction, article/paragraph boundary proposals, document classification,
  definitions, obligations, exceptions, actors, conditions, applicability,
  reference candidates, and draft dependency edges.
- **FR-022**: All model calls MUST go through the project's LLMClient /
  ModelProvider abstraction.
- **FR-023**: All LLM outputs MUST be constrained by Pydantic schemas and MUST
  pass schema validation before entering downstream output.
- **FR-024**: All extracted semantic fields MUST remain draft-only, and
  SemanticUnitDraft MUST keep review_status = needs_review.
- **FR-025**: LLM outputs MUST include evidence_text, ambiguity_notes,
  confidence, or validation findings where applicable.
- **FR-026**: Schema validation failures for LLM outputs MUST be reported in
  StructuringValidationReport or structured errors and MUST NOT silently enter
  the output.
- **FR-027**: The system MUST produce a StructuringValidationReport that reports
  unclear, incomplete, duplicated, contradictory, or suspicious parsing results.
- **FR-028**: Suspicious parsing results MUST be reported instead of silently
  accepted.
- **FR-029**: All outputs MUST be valid structured JSON and MUST pass the
  project's schema validation before they can be stored or handed to later
  workflows.
- **FR-030**: All outputs MUST serialize to JSON and parse back without losing
  document identity, document classification draft, source traceability,
  original text, temporal metadata, extraction provenance, explicit unit tree
  fields, document parse status, unit review status, semantic draft fields,
  dependency graph data, or validation warnings.
- **FR-031**: The pipeline MUST NOT output JudgmentResult records, formal
  RuleItem records, active RulePack records, or any final compliance
  conclusion.
- **FR-032**: The ComplianceJudgmentAgent MUST NOT be able to call this pipeline
  directly as a judgment tool.
- **FR-033**: Draft or unreviewed outputs MUST NOT be treated as official rules
  or active runtime rule packs.
- **FR-034**: Semantic relation kinds such as definition_applies,
  procedure_for, condition_for, and exception_to MUST remain schema-supported
  but optional/future extension points unless clear textual evidence supports
  them.
- **FR-035**: The system MUST NOT hard-code secrets, model settings, local file
  paths, or environment-specific configuration in the generated assets.
- **FR-036**: Logs and traces MUST NOT include secrets or unnecessary raw
  sensitive document text.
- **FR-037**: Each RegulationUnitDraft MUST include parent_unit_id,
  order_index, and display_label. HierarchyPath preserves source document
  labels, while parent_unit_id and order_index support explicit tree navigation
  and stable review UI rendering.
- **FR-038**: SemanticUnitDraft MUST support draft fields for trigger_events,
  required_actions, prohibited_actions, deadlines, thresholds, subject_scope,
  object_scope, and reporting_obligations. Populated semantic fields MUST remain
  draft-only, evidence-backed where applicable, and review_status = needs_review
  when produced by this feature.
- **FR-039**: StructuringPipelineOutput MUST include extraction provenance with
  extraction_method = deterministic, llm_assisted, or mixed, plus
  prompt_contract_version and model_trace_id when applicable. Provenance MUST NOT
  include secrets, full prompts, or unnecessary raw sensitive text.

### Constitution Alignment *(mandatory for Arbiter features)*

- **CA-001**: Feature scope is Admin parsing and shared regulation asset
  preparation. Runtime judgment is explicitly out of scope.
- **CA-002**: Runtime behavior MUST consume reviewed assets, reviewed rule packs,
  retrieval context, or explicitly marked test fixtures; it MUST NOT parse raw
  regulation files directly. Runtime MUST reject draft, needs_review, or
  missing-review-status assets unless execution mode is explicitly test.
- **CA-003**: Admin-side LLM-assisted structuring is in scope. All model calls
  MUST go through LLMClient / ModelProvider, all model outputs MUST be
  schema-constrained, and model outputs MUST remain draft / needs_review until
  human review.
- **CA-004**: Regulation assets and future runtime judgment drafts MUST preserve
  source version, effective date, expiration/repeal date, amendment or
  source-version relation, and as-of-date basis where available.
- **CA-005**: Future judgment drafts MUST cite stable regulation unit IDs, source
  document/version, article or clause number where available, and retrieval
  provenance. Free-text citation labels are insufficient.
- **CA-006**: Core outputs MUST be represented as JSON / Pydantic schemas,
  including RegulationDocumentDraft, DocumentClassificationDraft,
  RegulationUnitDraft, SemanticUnitDraft, ReferenceCandidate,
  DependencyEdgeDraft / RegulationUnitRelationDraft,
  ResolvedDependencyGraphDraft, StructuringValidationReport, and
  StructuringPipelineOutput.
- **CA-007**: Sensitive data, secrets, logs, traces, source text, extraction
  provenance, and human review status MUST have explicit handling requirements.
- **CA-008**: User-facing compliance outputs from this feature MUST remain
  reviewable structuring drafts and MUST NOT claim to replace final compliance
  decisions.

### Non-Goals

- This feature does not implement frontend UI, production asset store, asset
  promotion, production review workflow, runtime agent integration, active
  RulePack generation, formal RuleItem generation, JudgmentResult generation,
  or final compliance conclusions.
- LLM-assisted extraction is allowed for structuring and semantic extraction,
  but cannot produce formal rules or final compliance conclusions without human
  review.
- This feature defines only a minimal optional file-intake adapter boundary. It
  does not implement OCR, password handling, or full document layout recovery.

### Future Handoff Boundary

StructuringPipelineOutput is not runtime-safe. It is a draft preparation bundle
for human review and later promotion. A later review/promotion workflow must
convert approved drafts into reviewed runtime assets before Agent Runtime can
consume them. This feature only prepares draft assets and does not implement that
promotion workflow.

### Key Entities *(include if feature involves data)*

- **RegulationDocumentDraft**: A draft record for the submitted regulation or
  policy document, including document identity, source file, title when present,
  classification, status, relevant dates, temporal metadata, and parse_status.
- **TemporalMetadata**: Reviewable version and validity context, including
  version label, amendment history text, validity notes, temporal confidence,
  and ambiguity notes.
- **DocumentClassificationDraft**: A reviewable classification draft containing
  source type, issuer type/name, extensible categories/tags, evidence,
  ambiguity notes, and review_status.
- **RegulationUnitDraft**: A reviewable structured unit extracted from the
  source document, preserving hierarchy labels, explicit parent/order/display
  metadata, article metadata, source traceability, original text, semantic draft
  fields, and review_status.
- **ExtractionProvenance**: Bounded extraction metadata containing extraction
  method, prompt contract version, and model trace ID when applicable.
- **FileInput / ExtractedTextBundle**: Optional intake adapter boundary for
  future PDF/Word or upload workflows before NormalizedTextInput.
- **ReferenceCandidate**: A textual reference clue detected in source text before
  dependency resolution.
- **DependencyEdgeDraft / RegulationUnitRelationDraft**: A proposed resolved
  dependency edge between units, with evidence, confidence, ambiguity notes, and
  draft review state.
- **ResolvedDependencyGraphDraft**: A reviewable graph bundle containing
  reference candidates and proposed dependency edges.
- **StructuringValidationReport**: A report of warnings, errors, suspicious
  parsing results, unknown fields, duplicates, LLM schema validation failures,
  temporal ambiguity, provenance gaps, semantic draft issues, dependency graph
  issues, and other review needs.
- **StructuringPipelineOutput**: The complete draft output bundle that includes
  the document draft with classification, unit drafts, reference candidates,
  graph draft, and validation report.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a representative document with recognizable hierarchy, the
  reviewer receives a RegulationDocumentDraft and at least one RegulationUnitDraft
  for every recognizable article-level unit.
- **SC-002**: 100% of generated document drafts include
  parse_status = needs_review, 100% of document classification drafts include
  review_status = needs_review, 100% of generated semantic unit drafts include
  review_status = needs_review, 100% of generated unit drafts include
  review_status = needs_review, and 0 generated reviewable outputs use approved,
  rejected, or superseded.
- **SC-003**: 100% of generated outputs pass schema validation and JSON
  round-trip validation before being accepted as draft assets.
- **SC-004**: For test documents containing recognizable status or date text,
  status, version, amendment, validity, and relevant dates are either captured or
  explicitly marked unknown with validation findings or ambiguity notes.
- **SC-005**: For test documents containing duplicated article numbers,
  malformed hierarchy, or ambiguous references, the validation report flags the
  issue instead of silently accepting it.
- **SC-006**: For classification fields, semantic fields, and dependency edges
  that are populated, 100% of accepted fields are schema-constrained,
  draft-only, and traceable to evidence or validation findings.
- **SC-007**: Generated graph output separates ReferenceCandidate clues from
  DependencyEdgeDraft / RegulationUnitRelationDraft proposed edges.
- **SC-008**: 0 generated outputs contain JudgmentResult, active RulePack,
  formal RuleItem, or a final compliance conclusion.
- **SC-009**: Runtime judgment surfaces expose no direct action that lets
  ComplianceJudgmentAgent invoke the structuring pipeline.
- **SC-010**: A reviewer can inspect the source traceability and original text
  for any generated unit, and can render a stable tree using
  parent_unit_id/order_index/display_label without consulting the raw document
  parser.
- **SC-011**: Tests verify that model calls use LLMClient / ModelProvider and
  that schema-invalid model outputs become validation findings or structured
  errors rather than accepted draft data.
- **SC-012**: 100% of exported output bundles include extraction provenance
  without secrets, full prompts, or unnecessary raw sensitive text.

## Assumptions

- The submitter is an admin or compliance reviewer working in a controlled
  environment.
- Source files are regulation or internal policy documents, not arbitrary
  business scenario narratives.
- Source location may be page number, line number, paragraph index, heading
  path, or unknown depending on the source format.
- Promotion from draft assets to reviewed runtime-safe assets is outside this
  feature and requires a later human review workflow.
- A production-grade frontend is outside this feature; review can be supported
  by inspectable structured outputs shaped for later review UI rendering.
- PDF/Word handling is an optional intake adapter boundary only:
  FileInput -> ExtractedTextBundle -> NormalizedTextInput.
- First-scope extraction uses a hybrid strategy: deterministic code handles
  intake, source preservation, obvious structural hints, stable source_id /
  document_id linkage, JSON serialization, schema validation, and validation
  reports; LLM-assisted
  extraction handles variable-format structure, semantic fields, reference
  candidates, and draft dependency edges.
