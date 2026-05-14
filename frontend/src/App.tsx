import { useState, useCallback } from 'react'
import { StructuringOutputLoader } from './workbench/StructuringOutputLoader'
import { ValidationFailurePanel } from './workbench/ValidationFailurePanel'
import { DocumentMetadataPanel } from './workbench/DocumentMetadataPanel'
import { UnitTree } from './workbench/UnitTree'
import { UnitReviewPanel } from './workbench/UnitReviewPanel'
import { ReviewArtifactPanel } from './workbench/ReviewArtifactPanel'
import { ArtifactExportPanel } from './workbench/ArtifactExportPanel'
import type { SessionState } from './workbench/reviewSession'
import { useI18n } from './i18n/context'

type RightTab = 'review' | 'artifacts' | 'export'

function App() {
  const { t, lang, setLang } = useI18n()
  const [session, setSessionState] = useState<SessionState | null>(null)
  const [errors, setErrors] = useState<string[] | null>(null)
  const [selectedUnitId, setSelectedUnitId] = useState<string | null>(null)
  const [rightTab, setRightTab] = useState<RightTab>('review')

  const handleLoad = useCallback((s: SessionState) => {
    setSessionState(s)
    setErrors(null)
    setSelectedUnitId(null)
    setRightTab('review')
  }, [])

  const handleError = useCallback((errs: string[]) => {
    setErrors(errs)
    setSessionState(null)
  }, [])

  const handleDismiss = useCallback(() => {
    setErrors(null)
  }, [])

  const handleSessionChange = useCallback((s: SessionState) => {
    setSessionState(s)
  }, [])

  const handleReload = useCallback(() => {
    setSessionState(null)
    setErrors(null)
    setSelectedUnitId(null)
    setRightTab('review')
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <h1>{t.appTitle}</h1>
        <span className="badge">US1 MVP</span>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', flex: 1 }}>
          {t.appSubtitle}
        </span>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <select
            className="btn btn-sm"
            value={lang}
            onChange={(e) => setLang(e.target.value as 'zh' | 'en')}
            style={{ cursor: 'pointer' }}
          >
            <option value="zh">中文</option>
            <option value="en">English</option>
          </select>
          {session && (
            <button className="btn btn-sm" onClick={handleReload} data-testid="reload-document">
              {t.reloadDocument}
            </button>
          )}
        </div>
      </header>

      <main className="app-main">
        {errors && (
          <div className="workbench no-session">
            <ValidationFailurePanel errors={errors} onDismiss={handleDismiss} />
          </div>
        )}

        {!session && !errors && (
          <div className="workbench no-session">
            <StructuringOutputLoader onLoad={handleLoad} onError={handleError} />
          </div>
        )}

        {session && !errors && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', height: '100%' }}>
            <div style={{ flexShrink: 0, maxHeight: '220px', overflow: 'auto' }}>
              <DocumentMetadataPanel output={session.sourceOutput} />
            </div>
            <div className="workbench" style={{ flex: 1, minHeight: 0 }}>
              <UnitTree
                output={session.sourceOutput}
                selectedUnitId={selectedUnitId}
                onSelectUnit={setSelectedUnitId}
              />
              <div className="right-panel">
                <div className="tab-bar">
                  <button
                    className={rightTab === 'review' ? 'active' : ''}
                    onClick={() => setRightTab('review')}
                  >
                    {t.unitReview}
                  </button>
                  <button
                    className={rightTab === 'artifacts' ? 'active' : ''}
                    onClick={() => setRightTab('artifacts')}
                  >
                    {t.reviewArtifacts}
                  </button>
                  <button
                    className={rightTab === 'export' ? 'active' : ''}
                    onClick={() => setRightTab('export')}
                  >
                    {t.exportArtifacts}
                  </button>
                </div>
                <div className="tab-content">
                  {rightTab === 'review' && (
                    <UnitReviewPanel
                      output={session.sourceOutput}
                      session={session}
                      selectedUnitId={selectedUnitId}
                      onSessionChange={handleSessionChange}
                    />
                  )}
                  {rightTab === 'artifacts' && (
                    <ReviewArtifactPanel
                      session={session}
                      selectedUnitId={selectedUnitId}
                      onSessionChange={handleSessionChange}
                    />
                  )}
                  {rightTab === 'export' && (
                    <ArtifactExportPanel session={session} />
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
