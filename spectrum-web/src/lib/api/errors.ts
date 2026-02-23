/**
 * Structured error types for Spectrum API errors.
 */

export type ErrorCode =
  | 'BLOCKED_SOURCE'
  | 'NETWORK_ERROR'
  | 'CONTENT_EXTRACTION'
  | 'NOT_FOUND'
  | 'RATE_LIMITED'
  | 'AI_ERROR'
  | 'VALIDATION'
  | 'INTERNAL_ERROR'

export interface ApiErrorDetail {
  code: ErrorCode
  message: string
  suggestion: string
  retryable: boolean
  details?: Record<string, unknown>
}

export interface ApiErrorResponse {
  success: false
  error: ApiErrorDetail
}

/**
 * Enhanced error class with structured error information.
 */
export class SpectrumError extends Error {
  public readonly code: ErrorCode
  public readonly suggestion: string
  public readonly retryable: boolean
  public readonly details?: Record<string, unknown>

  constructor(errorDetail: ApiErrorDetail) {
    super(errorDetail.message)
    this.name = 'SpectrumError'
    this.code = errorDetail.code
    this.suggestion = errorDetail.suggestion
    this.retryable = errorDetail.retryable
    this.details = errorDetail.details
  }

  static fromApiResponse(response: ApiErrorResponse): SpectrumError {
    return new SpectrumError(response.error)
  }

  static networkError(message?: string): SpectrumError {
    return new SpectrumError({
      code: 'NETWORK_ERROR',
      message: message || 'Network connection failed',
      suggestion: 'Check your connection and try again in a moment.',
      retryable: true,
    })
  }

  static unknownError(message?: string): SpectrumError {
    return new SpectrumError({
      code: 'INTERNAL_ERROR',
      message: message || 'An unexpected error occurred',
      suggestion: 'Please try again.',
      retryable: true,
    })
  }
}

/**
 * Type guard to check if a response is a structured error.
 */
export function isApiErrorResponse(data: unknown): data is ApiErrorResponse {
  return (
    typeof data === 'object' &&
    data !== null &&
    'success' in data &&
    data.success === false &&
    'error' in data &&
    typeof (data as ApiErrorResponse).error === 'object' &&
    'code' in (data as ApiErrorResponse).error
  )
}
