import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { I18nProvider } from '../../src/i18n/context'
import { StructuringOutputLoader } from '../../src/workbench/StructuringOutputLoader'
import validFixture from '../../src/fixtures/structuring-output.valid.json'

const originalFetch = globalThis.fetch

function backendSuccess() {
  return {
    ok: true,
    json: async () => ({
      request_id: 'req-test',
      run_id: 'struct-run-test',
      status: 'succeeded',
      output: validFixture,
      errors: [],
      warnings: [],
      sanitized_trace: { adapter: '001-structuring', model_call_count: 1 },
      token_usage: null,
      completed_at: '2026-05-14T00:00:20Z',
    }),
  }
}

function renderLoader() {
  return render(
    <I18nProvider>
      <StructuringOutputLoader onLoad={vi.fn()} onError={vi.fn()} />
    </I18nProvider>,
  )
}

describe('StructuringOutputLoader Markdown run options', () => {
  beforeEach(() => {
    localStorage.setItem('arbiter-lang', 'en')
  })

  afterEach(() => {
    globalThis.fetch = originalFetch
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('sends llm_assisted=true by default for pasted Markdown', async () => {
    const fetchMock = vi.fn().mockResolvedValue(backendSuccess())
    globalThis.fetch = fetchMock
    renderLoader()

    fireEvent.change(screen.getByLabelText('Markdown Regulation Input'), {
      target: { value: '# Policy\n\nArticle 1\nContent.' },
    })
    fireEvent.click(screen.getByRole('button', { name: 'Create Draft From Markdown' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    const body = JSON.parse(String(fetchMock.mock.calls[0][1]?.body))
    expect(body.input.input_kind).toBe('markdown')
    expect(body.llm_assisted).toBe(true)
    expect(body.model_mode).toBe('configured_provider')
  })

  it('sends llm_assisted=false for uploaded Markdown when the expert disables LLM parsing', async () => {
    const fetchMock = vi.fn().mockResolvedValue(backendSuccess())
    globalThis.fetch = fetchMock
    const { container } = renderLoader()

    fireEvent.click(screen.getByRole('checkbox', { name: 'Use LLM-assisted parsing' }))
    const input = container.querySelector('input[type="file"]')
    if (!(input instanceof HTMLInputElement)) throw new Error('file input not found')

    const file = new File(['# Policy\n\nArticle 1\nContent.'], 'uploaded-policy.md', {
      type: 'text/markdown',
    })
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    const body = JSON.parse(String(fetchMock.mock.calls[0][1]?.body))
    expect(body.input.source_file).toBe('uploaded-policy.md')
    expect(body.llm_assisted).toBe(false)
    expect(body.model_mode).toBe('configured_provider')
  })
})
