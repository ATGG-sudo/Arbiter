import { describe, it, expect } from 'vitest'
import validFixture from '../../src/fixtures/structuring-output.valid.json'
import type { StructuringPipelineOutput, RegulationUnitDraft } from '../../src/contracts/structuringOutput'

describe('Unit tree ordering', () => {
  const output = validFixture as unknown as StructuringPipelineOutput

  it('has 10 units in fixture', () => {
    expect(output.units).toHaveLength(10)
  })

  it('preserves order_index sequence', () => {
    const orderIndices = output.units.map((u) => u.order_index)
    const sorted = [...orderIndices].sort((a, b) => a - b)
    expect(orderIndices).toEqual(sorted)
  })

  it('has correct parent-child relationships', () => {
    const rootUnits = output.units.filter((u) => u.parent_unit_id === null)
    expect(rootUnits.map((u) => u.unit_id)).toEqual([
      'unit-001',
      'unit-004',
      'unit-008',
    ])

    const childrenOf001 = output.units.filter(
      (u) => u.parent_unit_id === 'unit-001',
    )
    expect(childrenOf001.map((u) => u.unit_id)).toEqual([
      'unit-002',
      'unit-003',
    ])

    const childrenOf004 = output.units.filter(
      (u) => u.parent_unit_id === 'unit-004',
    )
    expect(childrenOf004.map((u) => u.unit_id)).toEqual([
      'unit-005',
      'unit-006',
      'unit-007',
    ])

    const childrenOf008 = output.units.filter(
      (u) => u.parent_unit_id === 'unit-008',
    )
    expect(childrenOf008.map((u) => u.unit_id)).toEqual([
      'unit-009',
      'unit-010',
    ])
  })

  it('children follow their parent in order_index', () => {
    const parentMap = new Map<string, RegulationUnitDraft>()
    for (const u of output.units) {
      parentMap.set(u.unit_id, u)
    }

    for (const unit of output.units) {
      if (unit.parent_unit_id) {
        const parent = parentMap.get(unit.parent_unit_id)
        expect(parent).toBeDefined()
        if (parent) {
          expect(unit.order_index).toBeGreaterThan(parent.order_index)
        }
      }
    }
  })

  it('each unit has a non-negative order_index', () => {
    for (const unit of output.units) {
      expect(unit.order_index).toBeGreaterThanOrEqual(0)
    }
  })

  it('display_labels are present for all units', () => {
    for (const unit of output.units) {
      expect(unit.display_label).toBeTruthy()
    }
  })
})
