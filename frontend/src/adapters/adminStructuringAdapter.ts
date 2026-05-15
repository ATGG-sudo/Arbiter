import {
  StructuringRunResult as StructuringRunResultSchema,
  type StructuringRunRequest,
  type StructuringRunResult,
} from '../contracts/structuringOutput'

/**
 * Admin structuring adapter client.
 *
 * Sends StructuringRunRequest to the local 001 backend HTTP endpoint and
 * accepts only schema-valid StructuringRunResult responses. The frontend does
 * not import provider SDKs, read API keys, implement prompt logic, or fallback
 * to UI-local structuring when the 001 adapter fails.
 */

const API_ENDPOINT = '/api/structuring/run'

function failureResult(
  request: StructuringRunRequest,
  code: string,
  message: string,
  status: StructuringRunResult['status'] = 'failed',
): StructuringRunResult {
  return {
    request_id: request.request_id,
    run_id: `struct-run-client-${Date.now()}`,
    status,
    output: null,
    errors: [{ code, message }],
    warnings: [],
    sanitized_trace: {
      adapter: '001-structuring',
      model_call_count: 0,
      validation_summary: {
        error_count: 1,
        warning_count: 0,
        info_count: 0,
      },
      redaction_warnings: [],
    },
    token_usage: null,
    completed_at: new Date().toISOString(),
  }
}

async function readJsonSafely(res: Response): Promise<unknown> {
  try {
    return await res.json()
  } catch {
    return null
  }
}

export async function runStructuringFromMarkdown(
  request: StructuringRunRequest,
): Promise<StructuringRunResult> {
  try {
    const res = await fetch(API_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request),
    })
    const payload = await readJsonSafely(res)
    const parsed = StructuringRunResultSchema.safeParse(payload)
    if (parsed.success) {
      return parsed.data
    }
    if (!res.ok) {
      return failureResult(
        request,
        'backend_structuring_run_failed',
        `Admin structuring adapter returned HTTP ${res.status}`,
      )
    }
    return failureResult(
      request,
      'invalid_structuring_run_result',
      'Admin structuring adapter returned a schema-invalid result',
      'validation_failed',
    )
  } catch (error) {
    return failureResult(
      request,
      'backend_structuring_run_unreachable',
      error instanceof Error ? error.message : String(error),
    )
  }
}
