import { describe, expect, it } from 'vitest'
import { StructuringPipelineOutput } from '../../src/contracts/structuringOutput'
import { IntegratedStructuringReviewPackage } from '../../src/contracts/reviewArtifacts'
import { structureMarkdownForReview } from '../../src/adapters/markdownStructuringAdapter'
import {
  createIntegratedStructuringReviewPackage,
  createReviewPatch,
} from '../../src/workbench/exportArtifacts'
import type { SessionState } from '../../src/workbench/reviewSession'

const markdown = `# 投资管理制度

第一章 总则

第一条 公司对外投资应履行审批程序。

第二条 投资发展部负责准备投资材料。`

describe('Markdown intake and integrated package export', () => {
  it('converts Markdown into a draft StructuringPipelineOutput for review', () => {
    const output = structureMarkdownForReview(
      markdown,
      'investment-policy.md',
      '2026-05-14T00:00:00Z',
    )

    const result = StructuringPipelineOutput.safeParse(output)
    expect(result.success).toBe(true)
    expect(output.document.source_file).toBe('investment-policy.md')
    expect(output.document.review_status).toBe('needs_review')
    expect(output.units.length).toBeGreaterThanOrEqual(3)
    expect(output.units.some((unit) => unit.unit_kind === 'article')).toBe(true)
    expect(output.units.every((unit) => unit.review_status === 'needs_review')).toBe(true)
  })

  it('exports a validated integrated package with immutable base output and patched merged output', () => {
    const output = structureMarkdownForReview(
      markdown,
      'investment-policy.md',
      '2026-05-14T00:00:00Z',
    )
    const unit = output.units.find((candidate) => candidate.unit_kind === 'article')
    expect(unit).toBeDefined()
    if (!unit) throw new Error('Expected an article unit')

    const sourceOutputRef = {
      contract_version: output.contract_version,
      document_id: output.document.document_id,
      source_id: output.document.source_id,
      source_file: output.document.source_file,
      loaded_at: '2026-05-14T00:00:00Z',
    }
    const patch = createReviewPatch(
      sourceOutputRef,
      {
        targetType: 'semantic_draft',
        targetId: `${unit.unit_id}.semantic_draft.summary`,
        unitId: unit.unit_id,
        fieldPath: 'semantic_draft.summary',
        oldValue: unit.semantic_draft.summary,
        newValue: '专家修订后的审批程序摘要',
        reviewerNote: '专家修订摘要字段',
        reviewerDecision: 'needs_changes',
        reviewerIdentity: null,
      },
      '2026-05-14T00:05:00Z',
    )
    const session: SessionState = {
      sourceOutput: output,
      sourceOutputRef,
      inputKind: 'markdown',
      sourceMarkdown: markdown,
      patchMap: new Map([[`${unit.unit_id}::semantic_draft.summary`, patch]]),
      decisions: [],
      curationRecords: [],
    }

    const pkg = createIntegratedStructuringReviewPackage(
      session,
      '2026-05-14T00:06:00Z',
    )

    const result = IntegratedStructuringReviewPackage.safeParse(pkg)
    expect(result.success).toBe(true)
    expect(pkg.package_status).toBe('needs_review')
    expect(pkg.input_kind).toBe('markdown')
    expect(pkg.source_markdown).toBe(markdown)

    const baseUnit = pkg.base_output.units.find((candidate) => candidate.unit_id === unit.unit_id)
    const mergedUnit = pkg.merged_output.units.find((candidate) => candidate.unit_id === unit.unit_id)
    expect(baseUnit?.semantic_draft.summary).toBe(unit.semantic_draft.summary)
    expect(mergedUnit?.semantic_draft.summary).toBe('专家修订后的审批程序摘要')
    expect(output.units.find((candidate) => candidate.unit_id === unit.unit_id)?.semantic_draft.summary)
      .toBe(unit.semantic_draft.summary)
  })
})
