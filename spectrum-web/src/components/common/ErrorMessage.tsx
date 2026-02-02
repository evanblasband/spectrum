interface ErrorMessageProps {
  message: string
  onRetry?: () => void
  className?: string
}

export function ErrorMessage({ message, onRetry, className = '' }: ErrorMessageProps) {
  return (
    <div
      className={`p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg ${className}`}
    >
      <p className="text-red-700 dark:text-red-400">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-2 text-sm text-red-600 dark:text-red-400 underline hover:no-underline"
        >
          Try again
        </button>
      )}
    </div>
  )
}
