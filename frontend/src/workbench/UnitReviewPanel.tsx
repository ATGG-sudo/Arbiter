import { useState, useCallback } from 'react'
import type { StructuringPipelineOutput, SemanticUnitDraft } from '../contracts/structuringOutput'
import type { SessionState } from './reviewSession'
import { recordPatch } from './reviewSession'
import { useI18n } from '../i18n/context'

interface UnitReviewPanelProps {
  output: StructuringPipelineOutput
  session: SessionState
  selectedUnitId: string | null
  onSessionChange: (session: SessionState) => void
}

function getSemanticFieldKeys(): (keyof SemanticUnitDraft)[] {
  return [
    'unit_type',
    'normalized_title',
    'summary',
    'definitions',
    'obligations',
    'exceptions',
    'applicability',
    'actors',
    'conditions',
    'trigger_events',
    'required_actions',
    'prohibited_actions',
    'deadlines',
    'thresholds',
    'subject_scope',
    'object_scope',
    'reporting_obligations',
    'evidence_text',
    'confidence',
    'review_status',
    'ambiguity_notes',
  ]
}

const IMPORTANT_FIELDS = new Set<keyof SemanticUnitDraft>([
  'summary',
  'obligations',
  'definitions',
  'exceptions',
  'conditions',
  'required_actions',
  'prohibited_actions',
  'thresholds',
  'deadlines',
])

function formatFieldValue(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'number') return String(value)
  if (Array.isArray(value)) return value.join('\n')
  return String(value)
}

function parseFieldValue(text: string, original: unknown): unknown {
  if (Array.isArray(original)) {
    return text.split('\n').filter((s) => s.trim() !== '')
  }
  if (typeof original === 'number') {
    const parsed = parseFloat(text)
    return isNaN(parsed) ? null : parsed
  }
  return text
}

export const UnitReviewPanel: React.FC<UnitReviewPanelProps> = ({
  output,
  session,
  selectedUnitId,
  onSessionChange,
}) => {
  const { t } = useI18n()
  const unit = selectedUnitId
    ? output.units.find((u) => u.unit_id === selectedUnitId)
    : null

  const [reviewerNote, setReviewerNote] = useState('')

  const handleSemanticEdit = useCallback(
    (field: keyof SemanticUnitDraft, text: string) => {
      if (!unit) return
      const originalValue = unit.semantic_draft[field]
      const newValue = parseFieldValue(text, originalValue)
      const fieldPath = `semantic_draft.${field}`
      const newSession = recordPatch(
        session,
        unit.unit_id,
        'semantic_draft',
        `${unit.unit_id}.${fieldPath}`,
        fieldPath,
        originalValue,
        newValue,
        reviewerNote,
        'needs_changes',
      )
      onSessionChange(newSession)
    },
    [unit, session, reviewerNote, onSessionChange],
  )

  if (!unit) {
    return (
      <div className="panel">
        <div className="panel-header">{t.unitReview}</div>
        <div className="panel-body">
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
              padding: '2rem 1rem',
              color: 'var(--text-muted)',
              textAlign: 'center',
            }}
          >
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ opacity: 0.4 }}>
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
            <div style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-secondary)' }}>
              {t.selectUnitPrompt}
            </div>
            <div style={{ fontSize: '0.8rem' }}>
              {t.selectUnitDetail}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const unitFindings = output.validation_report.findings.filter(
    (f) => f.unit_id === unit.unit_id || f.target_id?.startsWith(unit.unit_id),
  )

  const e = t.enum

  return (
    <div className="panel">
      <div className="panel-header">
        <span>{unit.display_label ?? unit.unit_id}</span>
        <span style={{ color: 'var(--text-muted)', fontWeight: 400, fontSize: '0.75rem' }}>
          {e.unitKind[unit.unit_kind] ?? unit.unit_kind}
        </span>
      </div>
      <div className="panel-body">
        <div className="unit-info-bar">
          <div className="info-item">
            <label>{t.unitId}:</label>
            <span className="value">{unit.unit_id}</span>
          </div>
          <div className="info-item">
            <label>{t.orderIndex}:</label>
            <span className="value">{unit.order_index}</span>
          </div>
          <div className="info-item">
            <label>{t.reviewStatus}:</label>
            <span className="value">{e.reviewStatus[unit.review_status] ?? unit.review_status}</span>
          </div>
          <div className="info-item">
            <label>{t.source}:</label>
            <span className="value">{unit.source_location.kind} {unit.source_location.value ?? ''}</span>
          </div>
        </div>

        <div className="review-section">
          <h3>{t.originalText}</h3>
          <div className="text-highlight">
            <pre style={{ background: 'transparent', border: 'none', padding: 0, maxHeight: 'none' }}>
              {unit.original_text}
            </pre>
          </div>
        </div>

        <div className="review-section">
          <h3>{t.normalizedText}</h3>
          <pre>{unit.normalized_text ?? t.notProvided}</pre>
        </div>

        <div className="review-section">
          <h3>{t.evidenceText}</h3>
          <pre>
            {unit.semantic_draft.evidence_text.length > 0
              ? unit.semantic_draft.evidence_text.join('\n---\n')
              : t.none}
          </pre>
        </div>

        {unitFindings.length > 0 && (
          <div className="review-section">
            <h3>{t.validationFindings}</h3>
            {unitFindings.map((f, i) => (
              <div key={i} className="validation-finding">
                <span className={`severity ${f.severity}`}>{e.severity[f.severity] ?? f.severity}</span>
                <span>{f.message}</span>
              </div>
            ))}
          </div>
        )}

        <div className="review-section">
          <h3>{t.reviewerNote}</h3>
          <textarea
            rows={2}
            value={reviewerNote}
            onChange={(e) => setReviewerNote(e.target.value)}
            placeholder={t.reviewerNotePlaceholder}
          />
        </div>

        <div className="review-section">
          <h3>{t.semanticDraftFields}</h3>
          {getSemanticFieldKeys().map((field) => {
            const originalValue = unit.semantic_draft[field]
            const patchKey = `${unit.unit_id}::semantic_draft.${field}`
            const patch = session.patchMap.get(patchKey)
            const currentValue = patch ? patch.new_value : originalValue
            const isImportant = IMPORTANT_FIELDS.has(field)
            return (
              <div key={field} style={{ marginBottom: '0.75rem' }}>
                <span className={`semantic-field-key ${isImportant ? 'important' : ''}`}>
                  {t.semanticField[field] ?? field}
                  {patch && (
                    <span
                      style={{
                        marginLeft: '0.4rem',
                        color: 'var(--needs-review-text)',
                        fontSize: '0.65rem',
                        fontWeight: 400,
                      }}
                    >
                      {t.modified}
                    </span>
                  )}
                </span>
                <textarea
                  rows={Array.isArray(originalValue) ? 3 : 2}
                  value={formatFieldValue(currentValue)}
                  onChange={(e) => handleSemanticEdit(field, e.target.value)}
                  style={isImportant ? { borderColor: '#d0d7de', backgroundColor: '#ffffff' } : {}}
                />
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
