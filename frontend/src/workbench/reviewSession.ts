import type { StructuringPipelineOutput } from '../contracts/structuringOutput'
import type {
  StructuringReviewPatch,
  StructuringReviewDecision,
  AssetCurationRecord,
  ReviewTargetType,
  ReviewDecision,
  CurationNoteType,
  WorkbenchInputKind,
} from '../contracts/reviewArtifacts'
import {
  createReviewPatch,
  createReviewDecision,
  createCurationRecord,
} from './exportArtifacts'

export interface SessionState {
  sourceOutput: Readonly<StructuringPipelineOutput>
  sourceOutputRef: {
    contract_version: string
    document_id: string
    source_id: string
    source_file: string
    loaded_at: string
  }
  inputKind: WorkbenchInputKind
  sourceMarkdown: string | null
  // Latest consolidated patch per field key (unitId + fieldPath)
  patchMap: Map<string, StructuringReviewPatch>
  decisions: StructuringReviewDecision[]
  curationRecords: AssetCurationRecord[]
}

export type SessionListener = (session: SessionState | null) => void

let currentSession: SessionState | null = null
let listeners: SessionListener[] = []

export function getSession(): SessionState | null {
  return currentSession
}

export function setSession(session: SessionState | null): void {
  currentSession = session
  for (const listener of listeners) {
    listener(currentSession)
  }
}

export function subscribe(listener: SessionListener): () => void {
  listeners.push(listener)
  return () => {
    listeners = listeners.filter((l) => l !== listener)
  }
}

function makeFieldKey(unitId: string | null, fieldPath: string): string {
  return `${unitId ?? 'doc'}::${fieldPath}`
}

export function recordPatch(
  session: SessionState,
  unitId: string | null,
  targetType: ReviewTargetType,
  targetId: string,
  fieldPath: string,
  oldValue: unknown,
  newValue: unknown,
  reviewerNote: string,
  reviewerDecision: ReviewDecision,
): SessionState {
  const key = makeFieldKey(unitId, fieldPath)
  const patch = createReviewPatch(session.sourceOutputRef, {
    targetType,
    targetId,
    unitId,
    fieldPath,
    oldValue,
    newValue,
    reviewerNote,
    reviewerDecision,
    reviewerIdentity: null,
  })
  const newMap = new Map(session.patchMap)
  newMap.set(key, patch)
  return {
    ...session,
    patchMap: newMap,
  }
}

export function recordDecision(
  session: SessionState,
  targetType: ReviewTargetType,
  targetId: string,
  unitId: string | null,
  reviewerDecision: ReviewDecision,
  reviewerNote: string,
): SessionState {
  const decision = createReviewDecision(session.sourceOutputRef, {
    targetType,
    targetId,
    unitId,
    reviewerDecision,
    reviewerNote,
    reviewerIdentity: null,
  })
  return {
    ...session,
    decisions: [...session.decisions, decision],
  }
}

export function recordCuration(
  session: SessionState,
  noteType: CurationNoteType,
  targetType: ReviewTargetType | undefined,
  targetId: string | undefined,
  unitId: string | null,
  note: string,
): SessionState {
  const curationId = `curation-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`
  const record = createCurationRecord(
    session.sourceOutputRef,
    {
      noteType,
      targetType,
      targetId,
      unitId,
      note,
      reviewerIdentity: null,
    },
    curationId,
  )
  return {
    ...session,
    curationRecords: [...session.curationRecords, record],
  }
}

export function getAllPatches(session: SessionState): StructuringReviewPatch[] {
  return Array.from(session.patchMap.values())
}
