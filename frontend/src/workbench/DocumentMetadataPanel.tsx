import type { StructuringPipelineOutput } from '../contracts/structuringOutput'
import { useI18n } from '../i18n/context'

interface DocumentMetadataPanelProps {
  output: StructuringPipelineOutput
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'number') return String(value)
  if (typeof value === 'boolean') return String(value)
  if (Array.isArray(value)) {
    if (value.length === 0) return ''
    return value.join(', ')
  }
  return JSON.stringify(value)
}

function MetadataItem({
  label,
  value,
  fullWidth = false,
}: {
  label: string
  value: unknown
  fullWidth?: boolean
}) {
  const { t } = useI18n()
  const str = formatValue(value)
  return (
    <div className={`metadata-item ${fullWidth ? 'full-width' : ''}`}>
      <label>{label}</label>
      <div className={`value ${!str ? 'incomplete' : ''}`}>
        {str || t.incomplete}
      </div>
    </div>
  )
}

export const DocumentMetadataPanel: React.FC<DocumentMetadataPanelProps> = ({
  output,
}) => {
  const { t } = useI18n()
  const doc = output.document
  const e = t.enum

  return (
    <div className="panel">
      <div className="panel-header">{t.documentMetadata}</div>
      <div className="panel-body">
        <div className="metadata-grid">
          <MetadataItem label={t.title} value={doc.title} />
          <MetadataItem label={t.documentNumber} value={doc.document_number} />
          <MetadataItem label={t.status} value={e.documentStatus[doc.document_status] ?? doc.document_status} />
          <MetadataItem label={t.reviewStatus} value={e.reviewStatus[doc.review_status] ?? doc.review_status} />
          <MetadataItem label={t.parseStatus} value={e.parseStatus[doc.parse_status] ?? doc.parse_status} />
          <MetadataItem label={t.effectiveDate} value={doc.effective_date} />
          <MetadataItem label={t.promulgationDate} value={doc.promulgation_date} />
          <MetadataItem label={t.repealDate} value={doc.repeal_date} />
          <MetadataItem label={t.versionLabel} value={doc.temporal_metadata.version_label} />
          <MetadataItem label={t.sourceType} value={e.sourceType[doc.classification.source_type] ?? doc.classification.source_type} />
          <MetadataItem label={t.issuerType} value={e.issuerType[doc.classification.issuer_type] ?? doc.classification.issuer_type} />
          <MetadataItem label={t.issuerName} value={doc.classification.issuer_name} />
          <MetadataItem label={t.confidence} value={doc.classification.confidence} />
        </div>

        {doc.warnings.length > 0 && (
          <div className="review-section" style={{ marginTop: '0.75rem' }}>
            <h3>{t.documentWarnings}</h3>
            <ul className="warnings-list">
              {doc.warnings.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        )}

        {output.validation_report.findings.filter((f) => f.target_type === 'document').length > 0 && (
          <div className="review-section" style={{ marginTop: '0.75rem' }}>
            <h3>{t.validationFindings}</h3>
            {output.validation_report.findings
              .filter((f) => f.target_type === 'document')
              .map((f, i) => (
                <div key={i} className="validation-finding">
                  <span className={`severity ${f.severity}`}>{e.severity[f.severity] ?? f.severity}</span>
                  <span>{f.message}</span>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  )
}
