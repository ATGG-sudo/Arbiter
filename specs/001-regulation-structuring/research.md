# Phase 0 Research: Regulation Structuring Pipeline

## Decision: Use hybrid deterministic + LLM-assisted extraction for the first implementation

**Rationale**: Deterministic code is needed for repeatability, source
preservation, stable source_id / document_id linkage, obvious structural hints,
JSON serialization, schema validation, and validation reports. Real internal
policies and external regulations have inconsistent formats, so deterministic
rules alone are insufficient for variable-format hierarchy interpretation,
semantic unit extraction, article/paragraph boundary proposals, document
classification, definitions, obligations, exceptions, actors, conditions,
applicability, reference candidates, and draft dependency edges. LLM-assisted
outputs must be Pydantic-constrained, evidence-backed where applicable, and
remain draft / needs_review until human review.

**Alternatives considered**: Deterministic-only structuring was rejected because
it cannot handle enough real-world format variation. LLM-only extraction was
rejected because it weakens source traceability, repeatability, stable ID
linkage, fixture-based tests, and validation boundaries.

## Decision: Accept normalized text and Markdown as the primary input boundary

**Rationale**: The revised spec narrows direct input scope to already extracted
text and Markdown. This keeps the first implementation focused on structuring
and validation, not file extraction. PDF/Word handling is represented only as a
minimal optional adapter boundary: `FileInput -> ExtractedTextBundle ->
NormalizedTextInput`.

**Alternatives considered**: First-class PDF/Word parsing in the pipeline. This
was rejected for the first slice because document extraction libraries,
password-protected files, layout recovery, and OCR would expand scope beyond
the structuring contract.

## Decision: Expand review statuses but keep pipeline output needs_review

**Rationale**: Later review UI and promotion workflows need lifecycle states
such as `approved`, `rejected`, and `superseded`. The structuring pipeline is not
that workflow, so all reviewable outputs created here remain
`review_status = needs_review`.

**Alternatives considered**: Keeping only `needs_review` would make later
workflow schemas churn. Allowing this pipeline to assign approved/rejected states
was rejected because it would blur draft extraction with human review.

## Decision: Add a stable but extensible document classification draft

**Rationale**: The pipeline must distinguish external regulatory documents
from internal policies without freezing a detailed business or compliance-topic
taxonomy in the first slice. `DocumentSourceType` and `IssuerType` provide
coarse stable fields, while `DocumentCategory`, `topic_tags`, and
`classification_tags` preserve extensibility. All classification remains draft /
needs_review until a later review workflow confirms it.

**Alternatives considered**: A detailed enum tree for compliance topics was
rejected because it would prematurely lock business taxonomy. A single
`document_kind` string was rejected because it cannot carry issuer, evidence,
review state, or extensible tags cleanly.

## Decision: Define Pydantic schemas before parser and LLM behavior

**Rationale**: Deterministic parsing, LLM-assisted extraction, semantic draft
fields, reference candidates, and proposed dependency edges must write into the
same schema-backed draft models. Schemas are the review surface and validation
boundary. Free-form model prose is not allowed as primary output.

**Alternatives considered**: Free-form dictionaries or Markdown-only outputs.
These would hide business interfaces and weaken validation, review, and
round-trip guarantees.

## Decision: Separate document parse status from unit review status

**Rationale**: `RegulationDocumentDraft.parse_status` describes the parsing
state of the whole source document, while `RegulationUnitDraft.review_status`
describes human review state for each extracted unit. Keeping them separate
avoids implying that a parsed document and every unit share the same lifecycle.

**Alternatives considered**: One shared `review_status` field for all outputs.
This was rejected because it merges document-level parsing confidence with
unit-level review readiness.

## Decision: Add explicit unit tree fields beside HierarchyPath

**Rationale**: `HierarchyPath` preserves source labels such as chapter, section,
article, paragraph, and item. Later review UI rendering and runtime context
assembly also need explicit tree mechanics, so `RegulationUnitDraft` includes
`parent_unit_id`, `order_index`, and `display_label`.

**Alternatives considered**: Deriving the tree only from labels was rejected
because real documents have repeated labels, skipped levels, and inconsistent
numbering.

## Decision: Expand SemanticUnitDraft with scenario-oriented draft fields

**Rationale**: Scenario-based compliance judgment later needs more than generic
obligations. Draft semantic fields now include trigger events, required actions,
prohibited actions, deadlines, thresholds, subject scope, object scope, and
reporting obligations. These remain draft-only, evidence-backed where
applicable, and `needs_review` when produced by this feature.

**Alternatives considered**: Waiting until runtime design to add these fields was
rejected because reviewers need to inspect and correct the draft semantics before
they become runtime context.

## Decision: Add temporal metadata and extraction provenance

**Rationale**: Later runtime judgment needs version and validity context, while
reviewers need to know how draft fields were produced. `TemporalMetadata`
captures version label, amendment history text, validity notes, confidence, and
ambiguity. `ExtractionProvenance` captures deterministic, LLM-assisted, or mixed
extraction plus bounded prompt/model trace identifiers.

**Alternatives considered**: Keeping temporal notes as generic warnings was
rejected because date/version context is a first-class basis for compliance
interpretation. Storing full prompts or payloads was rejected because it risks
leaking secrets and sensitive raw text.

## Decision: Include a resolved dependency graph draft

**Rationale**: Regulation and policy units are not isolated; definitions,
exceptions, conditions, procedures, and cross-references can affect later
interpretation. The pipeline needs a dependency graph draft to support reviewer
navigation, context assembly, version impact analysis, later retrieval, and
future links between internal policy units and external regulation units.
Detected references and resolved dependencies must be separated. References are
first detected as candidates, and the pipeline may propose resolved dependency
edges when textual or model-extracted evidence supports them. Proposed edges
remain draft / needs_review unless approved. All relation kinds are draft
interpretations, and no edge is final legal meaning. Unresolved, ambiguous, or
low-confidence references must be preserved in the validation report.

**Required distinction**:
- `ReferenceCandidate` = textual reference clue
- `DependencyEdgeDraft` = proposed resolved edge between units
- `ReviewedDependencyEdge` = human-approved edge for downstream use

**Alternatives considered**: A model that stops at textual clues was rejected
because it does not support reviewable context assembly or dependency
navigation. Treating resolved edges as final was rejected because final legal
meaning requires human review.

## Decision: Validation report is part of the primary output

**Rationale**: Suspicious results must not be silently accepted. Validation must
cover deterministic parsing, LLM output validation, semantic draft extraction,
and dependency graph issues, including duplicate IDs, malformed hierarchy,
missing source provenance, schema-invalid LLM output, missing evidence,
unresolved references, ambiguous dependency edges, and circular references.

**Alternatives considered**: Raising exceptions for all anomalies. This would
make partially useful draft output unavailable and force reviewers to inspect
raw failures instead of structured warnings.

## Decision: JSON export is file-based and schema-backed

**Rationale**: The feature needs reviewable artifacts, not a database or
runtime service. File-based JSON keeps outputs inspectable and supports exact
schema round-trip tests.

**Alternatives considered**: Database persistence or web API endpoints. These
are unnecessary for this feature and belong to later asset management or review
workflow work.

## Decision: StructuringPipelineOutput is not runtime-safe

**Rationale**: The output bundle is a draft preparation artifact. A later
review/promotion workflow must convert approved drafts into reviewed runtime
assets before Agent Runtime can consume them.

**Alternatives considered**: Treating approved-looking fields inside the draft as
runtime-ready was rejected because it violates Admin/Runtime separation and the
review-status gate.

## Final Phase 0 Position

The offline/admin RegulationStructuringPipeline may produce only:
- RegulationDocumentDraft
- DocumentClassificationDraft
- RegulationUnitDraft
- SemanticUnitDraft
- ReferenceCandidate
- RegulationUnitRelationDraft / DependencyEdgeDraft
- ResolvedDependencyGraphDraft
- StructuringValidationReport
- ExtractionProvenance

The pipeline must not produce:
- JudgmentResult
- active RulePack
- formal RuleItem
- unvalidated LLM output
- final legal judgment
- runtime agent answer
- runtime-safe reviewed assets
