import { useRef, useCallback, useState } from 'react'
import { loadStructuringOutput } from '../validation/loadStructuringOutput'
import { runStructuringFromMarkdown } from '../adapters/adminStructuringAdapter'
import type { StructuringPipelineOutput } from '../contracts/structuringOutput'
import type { SessionState } from './reviewSession'
import { setSession } from './reviewSession'
import { deepFreeze } from './sessionState'
import { useI18n } from '../i18n/context'

interface StructuringOutputLoaderProps {
  onLoad: (session: SessionState) => void
  onError: (errors: string[]) => void
}

export const StructuringOutputLoader: React.FC<StructuringOutputLoaderProps> = ({
  onLoad,
  onError,
}) => {
  const { t } = useI18n()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [markdownText, setMarkdownText] = useState('')
  const [useLlmAssisted, setUseLlmAssisted] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  const openSession = useCallback(
    (
      output: StructuringPipelineOutput,
      sourceFile: string,
      inputKind: SessionState['inputKind'],
      sourceMarkdown: string | null,
    ) => {
      const session: SessionState = {
        sourceOutput: deepFreeze(structuredClone(output)),
        sourceOutputRef: {
          contract_version: output.contract_version,
          document_id: output.document.document_id,
          source_id: output.document.source_id,
          source_file: sourceFile,
          loaded_at: new Date().toISOString(),
        },
        inputKind,
        sourceMarkdown,
        patchMap: new Map(),
        decisions: [],
        curationRecords: [],
      }
      setSession(session)
      onLoad(session)
    },
    [onLoad],
  )

  const handleJsonText = useCallback(
    (text: string, sourceFile: string) => {
      try {
        const parsed = JSON.parse(text)
        const result = loadStructuringOutput(parsed)
        if (result.success) {
          openSession(result.data, sourceFile, 'structuring_output_json', null)
        } else {
          onError(result.errors)
        }
      } catch {
        onError([t.invalidJsonFile])
      }
    },
    [onError, openSession, t],
  )

  const handleMarkdownText = useCallback(
    async (text: string, sourceFile: string) => {
      setIsLoading(true)
      try {
        const request = {
          request_id: `req-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
          input: {
            input_kind: 'markdown' as const,
            source_id: `src-${Date.now()}`,
            source_file: sourceFile,
            raw_markdown: text,
            source_type: 'internal_policy' as const,
            metadata: {},
          },
          llm_assisted: useLlmAssisted,
          model_mode: 'configured_provider' as const,
          requested_at: new Date().toISOString(),
        }
        const result = await runStructuringFromMarkdown(request)
        if (result.status === 'succeeded' && result.output) {
          openSession(result.output, sourceFile, 'markdown', text)
        } else {
          const errorMessages = result.errors.map((e) =>
            typeof e.message === 'string' ? e.message : String(e),
          )
          onError(errorMessages.length > 0 ? errorMessages : [t.invalidMarkdownInput])
        }
      } catch (error) {
        onError([error instanceof Error ? error.message : t.invalidMarkdownInput])
      } finally {
        setIsLoading(false)
      }
    },
    [onError, openSession, t, useLlmAssisted],
  )

  const handleFile = useCallback(
    (file: File) => {
      const reader = new FileReader()
      reader.onload = () => {
        const content = String(reader.result ?? '')
        const name = file.name.toLowerCase()
        if (name.endsWith('.json') || file.type === 'application/json') {
          handleJsonText(content, file.name)
          return
        }
        if (name.endsWith('.md') || name.endsWith('.markdown')) {
          handleMarkdownText(content, file.name)
          return
        }
        onError([t.unsupportedInputFile])
      }
      reader.readAsText(file)
    },
    [handleJsonText, handleMarkdownText, onError, t],
  )

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      const file = e.dataTransfer.files[0]
      if (file) {
        handleFile(file)
      } else {
        onError([t.pleaseUploadSupportedFile])
      }
    },
    [handleFile, onError, t],
  )

  const onFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const onMarkdownSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault()
      await handleMarkdownText(markdownText, 'markdown-input.md')
    },
    [handleMarkdownText, markdownText],
  )

  return (
    <div className="loader-shell">
      <form className="markdown-loader" onSubmit={onMarkdownSubmit}>
        <label htmlFor="markdown-input">{t.markdownInput}</label>
        <textarea
          id="markdown-input"
          rows={10}
          value={markdownText}
          onChange={(e) => setMarkdownText(e.target.value)}
          placeholder={t.markdownInputPlaceholder}
        />
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={useLlmAssisted}
            onChange={(e) => setUseLlmAssisted(e.target.checked)}
          />
          <span>{t.useLlmAssistedParsing}</span>
        </label>
        <button
          className="btn btn-primary"
          type="submit"
          disabled={isLoading || !markdownText.trim()}
        >
          {isLoading ? t.parsingMarkdown : t.createDraftFromMarkdown}
        </button>
        {isLoading && (
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
            {t.parsingMarkdown}
          </p>
        )}
      </form>
      <div
        className="file-input-area"
        onClick={() => fileInputRef.current?.click()}
        onDrop={onDrop}
        onDragOver={(e) => e.preventDefault()}
        role="button"
        tabIndex={0}
        aria-label={t.dropSupportedHere}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".json,.md,.markdown,application/json,text/markdown"
          onChange={onFileChange}
        />
        <p>{t.dropSupportedHere}</p>
        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
          {t.supportedInputs}
        </p>
      </div>
    </div>
  )
}
