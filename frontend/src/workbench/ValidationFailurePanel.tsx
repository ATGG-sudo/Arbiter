import { useI18n } from '../i18n/context'

interface ValidationFailurePanelProps {
  errors: string[]
  onDismiss: () => void
}

export const ValidationFailurePanel: React.FC<ValidationFailurePanelProps> = ({
  errors,
  onDismiss,
}) => {
  const { t } = useI18n()
  return (
    <div className="validation-errors" role="alert" aria-live="assertive">
      <h2>{t.validationFailed}</h2>
      <p style={{ fontSize: '0.85rem', marginBottom: '0.75rem', color: 'var(--text-muted)' }}>
        {t.noSessionCreated}
      </p>
      <ul>
        {errors.map((err, i) => (
          <li key={i}>{err}</li>
        ))}
      </ul>
      <div style={{ marginTop: '1rem' }}>
        <button className="btn btn-primary btn-sm" onClick={onDismiss}>
          {t.dismiss}
        </button>
      </div>
    </div>
  )
}
