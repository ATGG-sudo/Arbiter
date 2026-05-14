import { useState } from 'react'
import type { SessionState } from './reviewSession'
import { recordDecision, recordCuration } from './reviewSession'
import type { ReviewTargetType, ReviewDecision, CurationNoteType } from '../contracts/reviewArtifacts'
import { useI18n } from '../i18n/context'

interface ReviewArtifactPanelProps {
  session: SessionState
  selectedUnitId: string | null
  onSessionChange: (session: SessionState) => void
}

const TARGET_TYPES: ReviewTargetType[] = [
  'document',
  'unit',
  'semantic_draft',
  'reference_candidate',
  'dependency_edge',
  'curation_note',
]

const DECISIONS: ReviewDecision[] = [
  'approved',
  'rejected',
  'needs_changes',
  'needs_more_evidence',
  'superseded',
]

const NOTE_TYPES: CurationNoteType[] = [
  'expert_note',
  'candidate_rule_hint',
  'scenario_example',
  'ambiguity_case',
  'dependency_issue',
]

export const ReviewArtifactPanel: React.FC<ReviewArtifactPanelProps> = ({
  session,
  selectedUnitId,
  onSessionChange,
}) => {
  const { t } = useI18n()
  const e = t.enum

  const [decTargetType, setDecTargetType] = useState<ReviewTargetType>('unit')
  const [decision, setDecision] = useState<ReviewDecision>('approved')
  const [decNote, setDecNote] = useState('')

  const [curNoteType, setCurNoteType] = useState<CurationNoteType>('expert_note')
  const [curTargetType, setCurTargetType] = useState<ReviewTargetType | ''>('')
  const [curNote, setCurNote] = useState('')

  const handleAddDecision = () => {
    const targetId = selectedUnitId ?? session.sourceOutputRef.document_id
    const newSession = recordDecision(
      session,
      decTargetType,
      targetId,
      selectedUnitId,
      decision,
      decNote,
    )
    onSessionChange(newSession)
    setDecNote('')
  }

  const handleAddCuration = () => {
    if (!curNote.trim()) return
    const targetId = selectedUnitId ?? session.sourceOutputRef.document_id
    const resolvedTargetType = curTargetType || undefined
    const resolvedTargetId = resolvedTargetType ? targetId : undefined
    const newSession = recordCuration(
      session,
      curNoteType,
      resolvedTargetType,
      resolvedTargetId,
      selectedUnitId,
      curNote,
    )
    onSessionChange(newSession)
    setCurNote('')
  }

  return (
    <div className="panel">
      <div className="panel-header">{t.reviewArtifacts}</div>
      <div className="panel-body">
        <div className="review-section">
          <h3>{t.recordDecision}</h3>
          <div className="curation-form">
            <select
              value={decTargetType}
              onChange={(ev) => setDecTargetType(ev.target.value as ReviewTargetType)}
            >
              {TARGET_TYPES.map((tt) => (
                <option key={tt} value={tt}>
                  {e.targetType[tt] ?? tt}
                </option>
              ))}
            </select>
            <select
              value={decision}
              onChange={(ev) => setDecision(ev.target.value as ReviewDecision)}
            >
              {DECISIONS.map((d) => (
                <option key={d} value={d}>
                  {e.decision[d] ?? d}
                </option>
              ))}
            </select>
            <textarea
              value={decNote}
              onChange={(ev) => setDecNote(ev.target.value)}
              placeholder={t.decisionRationalePlaceholder}
            />
            <button className="btn btn-sm" onClick={handleAddDecision}>
              {t.addDecision}
            </button>
          </div>
          {session.decisions.length > 0 && (
            <ul className="curation-list">
              {session.decisions.map((d, i) => (
                <li key={i}>
                  <div className="meta">
                    {e.targetType[d.target_type] ?? d.target_type} / {e.decision[d.reviewer_decision] ?? d.reviewer_decision} @{' '}
                    {new Date(d.reviewed_at).toLocaleString()}
                  </div>
                  {d.reviewer_note}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="review-section">
          <h3>{t.addExpertNote}</h3>
          <div className="curation-form">
            <select
              value={curNoteType}
              onChange={(ev) => setCurNoteType(ev.target.value as CurationNoteType)}
            >
              {NOTE_TYPES.map((nt) => (
                <option key={nt} value={nt}>
                  {e.noteType[nt] ?? nt}
                </option>
              ))}
            </select>
            <select
              value={curTargetType}
              onChange={(ev) => setCurTargetType(ev.target.value as ReviewTargetType | '')}
            >
              <option value="">{t.noTarget}</option>
              {TARGET_TYPES.map((tt) => (
                <option key={tt} value={tt}>
                  {e.targetType[tt] ?? tt}
                </option>
              ))}
            </select>
            <textarea
              value={curNote}
              onChange={(ev) => setCurNote(ev.target.value)}
              placeholder={t.notePlaceholder}
            />
            <button className="btn btn-sm" onClick={handleAddCuration}>
              {t.addExpertNote}
            </button>
          </div>
          {session.curationRecords.length > 0 && (
            <ul className="curation-list">
              {session.curationRecords.map((r, i) => (
                <li key={i}>
                  <div className="meta">
                    {e.noteType[r.note_type] ?? r.note_type} @ {new Date(r.created_at).toLocaleString()}
                    {r.target_type ? ` · ${e.targetType[r.target_type] ?? r.target_type}` : ''}
                  </div>
                  {r.note}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}
