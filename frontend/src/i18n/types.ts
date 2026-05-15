export type Lang = 'zh' | 'en'

export interface T {
  // App
  appTitle: string
  appSubtitle: string
  reloadDocument: string

  // Loader
  dropJsonHere: string
  onlyJsonAccepted: string
  dropSupportedHere: string
  supportedInputs: string
  markdownInput: string
  markdownInputPlaceholder: string
  useLlmAssistedParsing: string
  createDraftFromMarkdown: string
  invalidJsonFile: string
  invalidMarkdownInput: string
  pleaseUploadJson: string
  pleaseUploadSupportedFile: string
  unsupportedInputFile: string
  parsingMarkdown: string

  // Validation
  validationFailed: string
  noSessionCreated: string
  dismiss: string

  // Metadata
  documentMetadata: string
  title: string
  documentNumber: string
  status: string
  reviewStatus: string
  parseStatus: string
  effectiveDate: string
  promulgationDate: string
  repealDate: string
  versionLabel: string
  sourceType: string
  issuerType: string
  issuerName: string
  confidence: string
  documentWarnings: string
  validationFindings: string
  incomplete: string
  none: string
  notProvided: string

  // Unit Tree
  unitTree: string

  // Unit Review
  unitReview: string
  selectUnitPrompt: string
  selectUnitDetail: string
  originalText: string
  normalizedText: string
  sourceLocation: string
  evidenceText: string
  reviewerNote: string
  reviewerNotePlaceholder: string
  semanticDraftFields: string
  modified: string
  unitId: string
  orderIndex: string
  source: string

  // Review Artifacts
  reviewArtifacts: string
  recordDecision: string
  decisionRationalePlaceholder: string
  addDecision: string
  addExpertNote: string
  notePlaceholder: string
  noTarget: string

  // Export
  exportArtifacts: string
  sourceNotModified: string
  exportPatches: string
  exportDecisions: string
  exportNotes: string
  exportAll: string
  exportIntegratedPackage: string
  pendingPatches: string

  // Field labels
  semanticField: Record<string, string>

  // Enums
  enum: {
    reviewStatus: Record<string, string>
    documentStatus: Record<string, string>
    parseStatus: Record<string, string>
    unitKind: Record<string, string>
    sourceType: Record<string, string>
    issuerType: Record<string, string>
    severity: Record<string, string>
    targetType: Record<string, string>
    decision: Record<string, string>
    noteType: Record<string, string>
    semanticUnitType: Record<string, string>
  }
}
