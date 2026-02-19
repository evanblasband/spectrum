import { SpectrumError, ErrorCode } from '@/lib/api/errors'

interface ErrorMessageProps {
  error: Error | SpectrumError
  onRetry?: () => void
  className?: string
}

interface ErrorStyle {
  bg: string
  border: string
  text: string
  icon: string
}

const ERROR_STYLES: Record<ErrorCode, ErrorStyle> = {
  BLOCKED_SOURCE: {
    bg: 'bg-orange-50 dark:bg-orange-900/20',
    border: 'border-orange-200 dark:border-orange-800',
    text: 'text-orange-700 dark:text-orange-400',
    icon: '🚫',
  },
  NETWORK_ERROR: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/20',
    border: 'border-yellow-200 dark:border-yellow-800',
    text: 'text-yellow-700 dark:text-yellow-400',
    icon: '📡',
  },
  CONTENT_EXTRACTION: {
    bg: 'bg-amber-50 dark:bg-amber-900/20',
    border: 'border-amber-200 dark:border-amber-800',
    text: 'text-amber-700 dark:text-amber-400',
    icon: '📄',
  },
  NOT_FOUND: {
    bg: 'bg-gray-50 dark:bg-gray-800/50',
    border: 'border-gray-200 dark:border-gray-700',
    text: 'text-gray-700 dark:text-gray-400',
    icon: '🔍',
  },
  RATE_LIMITED: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    border: 'border-blue-200 dark:border-blue-800',
    text: 'text-blue-700 dark:text-blue-400',
    icon: '⏳',
  },
  AI_ERROR: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    border: 'border-purple-200 dark:border-purple-800',
    text: 'text-purple-700 dark:text-purple-400',
    icon: '🤖',
  },
  VALIDATION: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    border: 'border-red-200 dark:border-red-800',
    text: 'text-red-700 dark:text-red-400',
    icon: '⚠️',
  },
  INTERNAL_ERROR: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    border: 'border-red-200 dark:border-red-800',
    text: 'text-red-700 dark:text-red-400',
    icon: '❌',
  },
}

const DEFAULT_STYLE: ErrorStyle = {
  bg: 'bg-red-50 dark:bg-red-900/20',
  border: 'border-red-200 dark:border-red-800',
  text: 'text-red-700 dark:text-red-400',
  icon: '❌',
}

function isSpectrumError(error: Error): error is SpectrumError {
  return error instanceof SpectrumError || 'code' in error
}

export function ErrorMessage({ error, onRetry, className = '' }: ErrorMessageProps) {
  const isStructured = isSpectrumError(error)

  const code = isStructured ? (error as SpectrumError).code : 'INTERNAL_ERROR'
  const message = error.message
  const suggestion = isStructured ? (error as SpectrumError).suggestion : undefined
  const retryable = isStructured ? (error as SpectrumError).retryable : true

  const style = ERROR_STYLES[code] || DEFAULT_STYLE
  const showRetry = onRetry && retryable

  return (
    <div
      className={`p-4 ${style.bg} border ${style.border} rounded-lg ${className}`}
      role="alert"
    >
      <div className="flex items-start gap-3">
        <span className="text-xl" aria-hidden="true">
          {style.icon}
        </span>
        <div className="flex-1">
          <p className={`font-medium ${style.text}`}>{message}</p>
          {suggestion && (
            <p className={`mt-1 text-sm ${style.text} opacity-80`}>{suggestion}</p>
          )}
          {showRetry && (
            <button
              onClick={onRetry}
              className={`mt-3 px-4 py-2 text-sm font-medium rounded-md ${style.bg} ${style.text} border ${style.border} hover:opacity-80 transition-opacity`}
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
