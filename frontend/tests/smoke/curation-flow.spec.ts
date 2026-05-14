import { test, expect } from '@playwright/test'
import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const validFixturePath = path.resolve(__dirname, '../../src/fixtures/structuring-output.valid.json')
const zhFixturePath = path.resolve(__dirname, '../../src/fixtures/structuring-output.zh.json')

test.describe('US1 Curation Flow Smoke Test', () => {
  test('load valid fixture, browse units, edit semantic field, add expert note, export', async ({ page }) => {
    await page.goto('/')

    await expect(page.locator('text=Arbiter 审阅工作台')).toBeVisible()
    await expect(page.locator('text=US1 MVP')).toBeVisible()

    const fixtureContent = fs.readFileSync(validFixturePath, 'utf-8')
    const fileChooserPromise = page.waitForEvent('filechooser')
    await page.locator('[aria-label="点击或拖拽 Markdown 或 StructuringPipelineOutput JSON 文件到此处"]').click()
    const fileChooser = await fileChooserPromise
    await fileChooser.setFiles({
      name: 'structuring-output.valid.json',
      mimeType: 'application/json',
      buffer: Buffer.from(fixtureContent),
    })

    await expect(page.locator('text=文档元数据')).toBeVisible()
    await expect(page.locator('text=Investment Management Policy')).toBeVisible()
    await expect(page.locator('text=POL-INV-2026-001')).toBeVisible()

    await expect(page.locator('text=单元树')).toBeVisible()
    await expect(page.locator('text=Part I: General Provisions')).toBeVisible()

    await page.locator('button:has-text("Article 3: Pre-Investment Approval")').click()
    await expect(page.locator('text=No investment exceeding $1,000,000')).toBeVisible()
    await expect(page.locator('text=语义草稿字段')).toBeVisible()
    await expect(page.locator('text=单元编号:')).toBeVisible()

    const summaryTextarea = page.locator('text=summary').locator('xpath=../following-sibling::textarea')
    await summaryTextarea.fill('Updated: $1M threshold requires committee approval.')

    await page.locator('text=添加专家备注').first().scrollIntoViewIfNeeded()
    const curationTextarea = page.locator('text=添加专家备注').locator('xpath=../../textarea')
    await curationTextarea.fill('This threshold needs legal verification.')
    await page.locator('button:has-text("添加专家备注")').first().click()
    await expect(page.locator('text=This threshold needs legal verification.')).toBeVisible()

    const decisionNote = page.locator('text=记录判定').locator('xpath=../../textarea')
    await decisionNote.fill('Decision: needs more evidence on threshold applicability.')
    await page.locator('button:has-text("添加判定")').first().click()
    await expect(page.locator('text=Decision: needs more evidence on threshold applicability.')).toBeVisible()

    await expect(page.locator('[data-testid="export-all"]')).toBeVisible()
    await expect(page.locator('[data-testid="export-patches"]')).toBeEnabled()

    await page.locator('[data-testid="reload-document"]').click()
    await expect(page.locator('text=点击或拖拽')).toBeVisible()
  })

  test('load Chinese fixture and verify localized display', async ({ page }) => {
    await page.goto('/')

    const fixtureContent = fs.readFileSync(zhFixturePath, 'utf-8')
    const fileChooserPromise = page.waitForEvent('filechooser')
    await page.locator('[aria-label="点击或拖拽 Markdown 或 StructuringPipelineOutput JSON 文件到此处"]').click()
    const fileChooser = await fileChooserPromise
    await fileChooser.setFiles({
      name: 'structuring-output.zh.json',
      mimeType: 'application/json',
      buffer: Buffer.from(fixtureContent),
    })

    await expect(page.locator('text=文档元数据')).toBeVisible()
    await expect(page.locator('text=公司数据安全管理办法')).toBeVisible()
    await expect(page.locator('text=POL-SEC-2024-001')).toBeVisible()

    await expect(page.locator('text=单元树')).toBeVisible()
    await expect(page.locator('text=第一章 总则')).toBeVisible()

    await page.locator('button:has-text("第四条 访问控制")').click()
    await expect(page.locator('text=对核心数据的访问应当经过数据所有部门负责人及信息安全部双重审批')).toBeVisible()
    await expect(page.locator('text=语义草稿字段')).toBeVisible()
    await expect(page.locator('text=单元编号:')).toBeVisible()
    await expect(page.locator('text=待审阅')).toBeVisible()

    await page.locator('[data-testid="reload-document"]').click()
    await expect(page.locator('text=点击或拖拽')).toBeVisible()
  })

  test('switch language to English', async ({ page }) => {
    await page.goto('/')
    await page.locator('select').selectOption('en')
    await expect(page.locator('text=Arbiter Review Workbench')).toBeVisible()
    await expect(page.locator('text=Structuring Output Review')).toBeVisible()
  })

  test('invalid JSON shows validation failure and no session', async ({ page }) => {
    await page.goto('/')

    const invalidJson = JSON.stringify({ not_a_structuring_output: true })
    const fileChooserPromise = page.waitForEvent('filechooser')
    await page.locator('[aria-label="点击或拖拽 Markdown 或 StructuringPipelineOutput JSON 文件到此处"]').click()
    const fileChooser = await fileChooserPromise
    await fileChooser.setFiles({
      name: 'invalid.json',
      mimeType: 'application/json',
      buffer: Buffer.from(invalidJson),
    })

    await expect(page.locator('text=验证失败')).toBeVisible()
    await expect(page.locator('text=未创建可编辑的审阅会话')).toBeVisible()
    await expect(page.locator('text=文档元数据')).not.toBeVisible()
  })
})
