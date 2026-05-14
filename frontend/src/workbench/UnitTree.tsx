import type { StructuringPipelineOutput, ReviewStatus } from '../contracts/structuringOutput'
import { useI18n } from '../i18n/context'

interface UnitTreeProps {
  output: StructuringPipelineOutput
  selectedUnitId: string | null
  onSelectUnit: (unitId: string) => void
}

function buildTree(units: StructuringPipelineOutput['units']) {
  const sorted = [...units].sort((a, b) => a.order_index - b.order_index)
  const roots: typeof sorted = []
  const childrenByParent = new Map<string, typeof sorted>()

  for (const unit of sorted) {
    if (unit.parent_unit_id) {
      const list = childrenByParent.get(unit.parent_unit_id) ?? []
      list.push(unit)
      childrenByParent.set(unit.parent_unit_id, list)
    } else {
      roots.push(unit)
    }
  }

  return { roots, childrenByParent }
}

function StatusDot({ status }: { status: ReviewStatus }) {
  return <span className={`status-dot ${status}`} aria-hidden="true" />
}

export const UnitTree: React.FC<UnitTreeProps> = ({
  output,
  selectedUnitId,
  onSelectUnit,
}) => {
  const { t } = useI18n()
  const { roots, childrenByParent } = buildTree(output.units)

  const renderUnit = (unit: StructuringPipelineOutput['units'][number], depth: number) => {
    const children = childrenByParent.get(unit.unit_id) ?? []
    return (
      <li key={unit.unit_id}>
        <button
          className={selectedUnitId === unit.unit_id ? 'selected' : ''}
          onClick={() => onSelectUnit(unit.unit_id)}
          aria-pressed={selectedUnitId === unit.unit_id}
        >
          {Array.from({ length: depth }).map((_, i) => (
            <span key={i} className="indent" />
          ))}
          <StatusDot status={unit.review_status} />
          <span className="label" title={unit.display_label ?? unit.unit_id}>
            {unit.display_label ?? unit.unit_id}
          </span>
        </button>
        {children.length > 0 && (
          <ul className="unit-tree">{children.map((c) => renderUnit(c, depth + 1))}</ul>
        )}
      </li>
    )
  }

  return (
    <div className="panel" style={{ height: '100%' }}>
      <div className="panel-header">{t.unitTree}</div>
      <div className="panel-body">
        <ul className="unit-tree">{roots.map((u) => renderUnit(u, 0))}</ul>
      </div>
    </div>
  )
}
