import { useState, FormEvent } from 'react'

interface UrlInputFormProps {
  onSubmit: (url: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export function UrlInputForm({
  onSubmit,
  isLoading = false,
  disabled = false,
}: UrlInputFormProps) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    // Basic URL validation
    const trimmedUrl = url.trim()
    if (!trimmedUrl) {
      setError('Please enter a URL')
      return
    }

    try {
      const urlObj = new URL(trimmedUrl)
      if (!['http:', 'https:'].includes(urlObj.protocol)) {
        setError('URL must start with http:// or https://')
        return
      }
      onSubmit(trimmedUrl)
    } catch {
      setError('Please enter a valid URL')
    }
  }

  const inputClasses = [
    'w-full px-4 py-3 rounded-lg border',
    'bg-white dark:bg-gray-800',
    'text-gray-900 dark:text-white',
    'placeholder-gray-400',
    'focus:outline-none focus:ring-2 focus:ring-violet-500',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    error ? 'border-red-500' : 'border-gray-300 dark:border-gray-600',
  ].join(' ')

  const buttonClasses = [
    'px-6 py-3 rounded-lg font-medium',
    'bg-violet-600 hover:bg-violet-700',
    'text-white',
    'focus:outline-none focus:ring-2 focus:ring-violet-500 focus:ring-offset-2',
    'disabled:opacity-50 disabled:cursor-not-allowed',
    'transition-colors',
  ].join(' ')

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1">
          <label htmlFor="url-input" className="sr-only">
            Article URL
          </label>
          <input
            id="url-input"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Paste article URL here..."
            disabled={disabled}
            className={inputClasses}
          />
          {error && (
            <p className="mt-1 text-sm text-red-500">{error}</p>
          )}
        </div>
        <button
          type="submit"
          disabled={disabled || isLoading}
          className={buttonClasses}
        >
          {isLoading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {/* Example URLs */}
      <div className="mt-3 text-sm text-gray-500 dark:text-gray-400">
        <span>Try: </span>
        <button
          type="button"
          onClick={() => setUrl('https://apnews.com')}
          className="text-violet-600 hover:underline"
          disabled={disabled}
        >
          AP News
        </button>
        {' \u2022 '}
        <button
          type="button"
          onClick={() => setUrl('https://www.nytimes.com')}
          className="text-violet-600 hover:underline"
          disabled={disabled}
        >
          NY Times
        </button>
        {' \u2022 '}
        <button
          type="button"
          onClick={() => setUrl('https://www.foxnews.com')}
          className="text-violet-600 hover:underline"
          disabled={disabled}
        >
          Fox News
        </button>
      </div>
    </form>
  )
}
