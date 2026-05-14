import type { StructuringPipelineOutput } from '../contracts/structuringOutput'
import type {
  StructuringReviewPatch,
  StructuringReviewDecision,
  AssetCurationRecord,
  SourceOutputRef,
} from '../contracts/reviewArtifacts'

export interface ReviewSession {
  sourceOutput: Readonly<StructuringPipelineOutput>
  sourceOutputRef: SourceOutputRef
  patches: StructuringReviewPatch[]
  decisions: StructuringReviewDecision[]
  curationRecords: AssetCurationRecord[]
}

export interface UnitEditState {
  [unitId: string]: {
    semanticDraft?: Partial<Record<string, unknown>>
    reviewerNote?: string
  }
}

export function deepFreeze<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') return obj
  if (Object.isFrozen(obj)) return obj

  const propNames = Object.getOwnPropertyNames(obj)
  for (const name of propNames) {
    const value = (obj as Record<string, unknown>)[name]
    if (value !== null && typeof value === 'object') {
      deepFreeze(value)
    }
  }
  return Object.freeze(obj)
}

export function createReviewSession(
  output: StructuringPipelineOutput,
  sourceFile: string,
): ReviewSession {
  const now = new Date().toISOString()
  return {
    sourceOutput: deepFreeze(structuredClone(output)),
    sourceOutputRef: {
      contract_version: output.contract_version,
      document_id: output.document.document_id,
      source_id: output.document.source_id,
      source_file: sourceFile,
      loaded_at: now,
    },
    patches: [],
    decisions: [],
    curationRecords: [],
  }
}

export function getSourceValue(
  sourceOutput: StructuringPipelineOutput,
  unitId: string,
  fieldPath: string,
): unknown {
  const unit = sourceOutput.units.find((u) => u.unit_id === unitId)
  if (!unit) return undefined

  const parts = fieldPath.split('.')
  let current: unknown = unit
  for (const part of parts) {
    if (current && typeof current === 'object' && part in current) {
      current = (current as Record<string, unknown>)[part]
    } else {
      return undefined
    }
  }
  return current
}
