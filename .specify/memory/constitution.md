<!--
Sync Impact Report
Version change: 1.0.0 -> 1.1.0
Modified principles:
- I. Admin / Runtime Separation clarified to allow Admin-side LLM-assisted structuring
- II. Unified Model Access clarified for LLM-derived regulation assets
- III. Structured Data Contracts clarified for temporal and citation fields
- V. Auditable but Sanitized Logging renamed to VI. Citation, Evidence, and Sanitized Logging
- VI. Code Quality and Testability renumbered to VII. Code Quality and Testability
Added sections:
- V. Temporal Regulation Basis
Removed sections:
- None
Templates requiring updates:
- ✅ updated: .specify/templates/plan-template.md
- ✅ updated: .specify/templates/spec-template.md
- ✅ updated: .specify/templates/tasks-template.md
Follow-up TODOs: None
-->

# Arbiter Constitution

## Core Principles

### I. Admin / Runtime Separation

Regulation parsing and Agent Runtime MUST remain separate system surfaces.
Admin-side parsing and structuring modules convert PDF, Word, Markdown, or text
into draft structured regulation assets. Admin workflows MAY use LLM-assisted
semantic extraction because regulation and internal-policy formats are
heterogeneous and cannot be fully deterministic. LLM-derived regulation assets MUST remain draft artifacts with review_status = needs_review after schema validation,
and MUST NOT become reviewed runtime assets until human review or an approved promotion workflow confirms them.
Runtime modules MUST consume only reviewed regulation assets, reviewed rule
packs, and retrieval context. The ComplianceJudgmentAgent MUST NOT parse raw
regulation files directly and MUST NOT treat unreviewed draft assets as formal
judgment evidence.

Rationale: this boundary keeps draft extraction risk out of runtime compliance
judgments and makes human review status auditable.

### II. Unified Model Access

All model calls MUST pass through the shared LLMClient / ModelProvider
abstraction. Business modules MUST NOT hard-code model vendors, model names,
base URLs, or API keys. Model configuration MUST come from environment
variables or controlled configuration files. The model access layer MUST own
timeouts, retries, error handling, structured-output validation, and call trace
capture. LLM-derived regulation outputs MUST be schema-constrained and
reviewable before any downstream use. Tests MUST support a mock provider so unit
tests do not depend on real external model calls.

Rationale: centralized model access keeps provider changes replaceable and
prevents hidden live-model dependencies from entering business logic.

### III. Structured Data Contracts

Core module inputs and outputs MUST use structured JSON / Pydantic schemas.
Regulation assets, business scenarios, retrieval context, rule packs, judgment
results, citations, traces, and human review tasks MUST have explicit schemas.
Natural-language prompts MUST NOT become hidden business interfaces. Model
outputs MUST pass schema validation before entering later workflow stages.
Public APIs and internal service interfaces MUST expose stable, versioned,
schema-backed contracts and return structured JSON error responses.

Rationale: explicit contracts make intermediate artifacts reviewable,
versionable, and safe to exchange between deterministic code and model calls.

### IV. Secure Configuration

Configuration and secrets MUST come from environment variables or controlled
configuration files. Source code, tests, fixtures, and logs MUST NOT contain
real API keys, tokens, passwords, or private deployment secrets. The
`.env.example` file MAY list required variable names, but it MUST NOT contain
real secret values. Regulation files, internal rules, business scenarios, and
judgment records are sensitive by default. The system MUST prioritize local or
controlled-environment deployment paths.

Rationale: compliance and risk-control data is sensitive, and configuration
mistakes can leak both credentials and internal business facts.

### V. Temporal Regulation Basis

Regulation assets and runtime judgment drafts MUST preserve temporal basis where
available: source document version, effective date, expiration date, amendment or
source-version relationship, and the as-of date used for interpretation. Missing
temporal facts MUST be explicit instead of inferred silently.

Rationale: compliance answers can change when regulations are amended, expired,
or evaluated for a different date.

### VI. Citation, Evidence, and Sanitized Logging

Judgment drafts MUST cite stable regulation unit IDs, source document and
version, article or clause number where available, and retrieval provenance.
Free-text citation labels are insufficient. Runtime MUST reject draft,
needs_review, or missing-review-status regulation assets unless execution mode
is explicitly marked as test. Logs and traces MUST preserve auditability without
exposing unnecessary sensitive content. They MUST record key execution facts such
as document_id, unit_id, source version, validation results, error reasons,
review status, and retrieval provenance. Logs MUST NOT record API keys, tokens,
passwords, full sensitive business scenarios, or unnecessary raw file text. When
raw content is not needed for review, logs MUST use IDs, hashes, summaries, or
redacted excerpts.

Rationale: evidence is useful only when it is stable, reviewable, and safe to
inspect.

### VII. Code Quality and Testability

Core schemas, parsing rules, judgment boundaries, and security boundaries MUST
include necessary comments that explain design intent and edge conditions, not
surface-level code behavior. Core functionality MUST have tests covering schema
validation, regulation splitting, version and review-status recognition,
temporal basis handling, citation provenance, runtime review-status gates,
model-output validation, error paths, and security-sensitive behavior. Modules
MUST remain small, low-coupling, replaceable, and easy to roll back.

Rationale: this project handles regulated workflows, so correctness and
reviewability matter more than speculative flexibility.

## System Scope and Sensitive Data Constraints

Arbiter is an AI-assisted system for private fund compliance and risk-control
workflows. It supports regulation parsing, regulation asset management, rule
retrieval, compliance question answering, scenario-based compliance judgment,
and human review.
In this project, Arbiter refers to an AI-assisted private fund compliance and
risk-control system, not an autonomous legal or compliance decision maker.

Arbiter MUST NOT replace compliance personnel as the final decision maker. The
system produces traceable, auditable, reviewable judgment drafts and supporting
evidence. User-facing outputs MUST make draft status, source basis, validation
state, and human review status clear when they affect interpretation.

## Development Workflow and Quality Gates

Every feature plan MUST classify the work as Admin, Runtime, shared asset
management, or cross-cutting infrastructure. Plans that cross the Admin/Runtime
boundary MUST document the data handoff schema and review-status gate.

Every feature that touches model calls MUST route through LLMClient /
ModelProvider and include mock-provider test coverage. Every feature that
introduces or changes core data exchange MUST update the relevant schema and
include validation tests. Every feature that handles sensitive data, logging, or
configuration MUST include an explicit sanitization and secret-handling check.
Every feature that touches regulation assets or runtime judgment MUST preserve
temporal basis, stable citations, retrieval provenance, and review-status gates.

Implementation tasks MUST be scoped to small, reviewable increments. Unreviewed
draft extraction artifacts MAY be produced by Admin workflows, but Runtime
judgment tasks MUST reject draft / needs_review / missing-review-status assets
unless execution mode is explicitly marked as test.

## Governance

This constitution supersedes conflicting project practices, templates, and
feature-level plans. Amendments MUST include the changed text, the reason for
the change, the version bump classification, and any required template or
workflow updates.

Versioning follows semantic versioning. MAJOR changes remove or redefine a
principle in a backward-incompatible way. MINOR changes add principles,
sections, or materially expanded governance. PATCH changes clarify wording
without changing obligations.

All implementation plans MUST pass the Constitution Check before design work is
accepted and MUST re-check it before task generation. Reviews MUST verify
Admin/Runtime separation, model access boundaries, schema validation, temporal
basis, stable citation provenance, runtime review-status gates, secure
configuration, sanitized audit logging, and required tests before work is
treated as complete.

**Version**: 1.1.0 | **Ratified**: 2026-05-12 | **Last Amended**: 2026-05-13
