import { describe, it, expect } from 'vitest'
import validFixture from '../../src/fixtures/structuring-output.valid.json'
import type { StructuringPipelineOutput } from '../../src/contracts/structuringOutput'

describe('Document metadata review surface', () => {
  const output = validFixture as unknown as StructuringPipelineOutput

  it('has expected document fields', () => {
    expect(output.document.title).toBe('Investment Management Policy')
    expect(output.document.document_number).toBe('POL-INV-2026-001')
    expect(output.document.document_status).toBe('draft_for_comment')
    expect(output.document.parse_status).toBe('parsed')
    expect(output.document.review_status).toBe('needs_review')
  })

  it('has classification with source_type', () => {
    expect(output.document.classification.source_type).toBe('internal_policy')
    expect(output.document.classification.issuer_type).toBe('internal_org')
  })

  it('has temporal metadata', () => {
    expect(output.document.temporal_metadata.version_label).toBe('v1.0-draft')
    expect(output.document.temporal_metadata.effective_date_text).toBe('January 1, 2026')
  })

  it('has warnings array', () => {
    expect(output.document.warnings).toContain('Draft version not yet approved')
  })

  it('has validation report linked to document', () => {
    expect(output.validation_report.document_id).toBe(output.document.document_id)
    expect(output.validation_report.summary).toBeTruthy()
  })

  it('shows validation findings when present', () => {
    expect(output.validation_report.findings.length).toBeGreaterThan(0)
    const finding = output.validation_report.findings[0]
    expect(finding.severity).toBe('warning')
    expect(finding.message).toContain('confidence')
  })
})
