import type { SessionState } from './reviewSession'
import { getAllPatches } from './reviewSession'
import {
  createIntegratedStructuringReviewPackage,
  exportToJsonFile,
} from './exportArtifacts'
import { useI18n } from '../i18n/context'

interface ArtifactExportPanelProps {
  session: SessionState
}

export const ArtifactExportPanel: React.FC<ArtifactExportPanelProps> = ({
  session,
}) => {
  const { t } = useI18n()
  const patches = getAllPatches(session)

  const exportPatches = () => {
    exportToJsonFile(patches, 'structuring-review-patches.json')
  }

  const exportDecisions = () => {
    exportToJsonFile(session.decisions, 'structuring-review-decisions.json')
  }

  const exportCuration = () => {
    exportToJsonFile(session.curationRecords, 'asset-curation-records.json')
  }

  const exportAll = () => {
    exportToJsonFile(
      {
        source_output_ref: session.sourceOutputRef,
        patches,
        decisions: session.decisions,
        curation_records: session.curationRecords,
      },
      'review-session-artifacts.json',
    )
  }

  const exportIntegratedPackage = () => {
    exportToJsonFile(
      createIntegratedStructuringReviewPackage(session),
      'integrated-structuring-review-package.json',
    )
  }

  return (
    <div className="panel">
      <div className="panel-header">{t.exportArtifacts}</div>
      <div className="panel-body">
        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
          {t.sourceNotModified}
        </p>

        <div className="export-controls">
          <button
            className="btn btn-sm"
            onClick={exportPatches}
            disabled={patches.length === 0}
            data-testid="export-patches"
          >
            {t.exportPatches} ({patches.length})
          </button>
          <button
            className="btn btn-sm"
            onClick={exportDecisions}
            disabled={session.decisions.length === 0}
            data-testid="export-decisions"
          >
            {t.exportDecisions} ({session.decisions.length})
          </button>
          <button
            className="btn btn-sm"
            onClick={exportCuration}
            disabled={session.curationRecords.length === 0}
            data-testid="export-curation"
          >
            {t.exportNotes} ({session.curationRecords.length})
          </button>
          <button className="btn btn-sm btn-primary" onClick={exportAll} data-testid="export-all">
            {t.exportAll}
          </button>
          <button
            className="btn btn-sm btn-primary"
            onClick={exportIntegratedPackage}
            data-testid="export-integrated-package"
          >
            {t.exportIntegratedPackage}
          </button>
        </div>

        {patches.length > 0 && (
          <div className="review-section" style={{ marginTop: '0.75rem' }}>
            <h3>{t.pendingPatches}</h3>
            <ul className="curation-list">
              {patches.map((p, i) => (
                <li key={i}>
                  <div className="meta">
                    {p.field_path} → {p.reviewer_decision}
                  </div>
                  {p.reviewer_note}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
