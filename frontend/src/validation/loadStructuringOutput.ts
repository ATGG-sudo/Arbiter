import { z } from 'zod'
import { StructuringPipelineOutput } from '../contracts/structuringOutput'

export interface LoadResult {
  success: true
  data: z.infer<typeof StructuringPipelineOutput>
}

export interface LoadError {
  success: false
  errors: string[]
}

export type LoadOutputResult = LoadResult | LoadError

export function loadStructuringOutput(json: unknown): LoadOutputResult {
  const parseResult = StructuringPipelineOutput.safeParse(json)
  if (parseResult.success) {
    // Additional cross-field validation not covered by Zod
    const output = parseResult.data
    const errors: string[] = []

    if (output.validation_report.document_id !== output.document.document_id) {
      errors.push(
        `validation_report.document_id (${output.validation_report.document_id}) must match document.document_id (${output.document.document_id})`,
      )
    }

    if (output.dependency_graph.document_id !== output.document.document_id) {
      errors.push(
        `dependency_graph.document_id (${output.dependency_graph.document_id}) must match document.document_id (${output.document.document_id})`,
      )
    }

    for (const unit of output.units) {
      if (unit.document_id !== output.document.document_id) {
        errors.push(
          `unit.document_id (${unit.document_id}) must match document.document_id (${output.document.document_id})`,
        )
      }
    }

    for (const candidate of output.reference_candidates) {
      if (candidate.document_id !== output.document.document_id) {
        errors.push(
          `reference_candidate.document_id (${candidate.document_id}) must match document.document_id (${output.document.document_id})`,
        )
      }
    }

    if (errors.length > 0) {
      return { success: false, errors }
    }

    return { success: true, data: output }
  }

  const zodErrors = parseResult.error.errors.map(
    (e) => `${e.path.join('.')}: ${e.message}`,
  )
  return { success: false, errors: zodErrors }
}
