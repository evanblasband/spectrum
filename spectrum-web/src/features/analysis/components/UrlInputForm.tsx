import { useState, FormEvent, useRef, useEffect } from 'react'
import { useSearchHistory, type SearchHistoryItem } from '@/stores/useSearchHistory'
import { useSourceCompatibility } from '@/hooks/useSourceCompatibility'
import { SourceInfoPopover } from '@/components/common/SourceInfoPopover'

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
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const { history, removeFromHistory, clearHistory } = useSearchHistory()
  const { data: sourceData } = useSourceCompatibility()

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setShowDropdown(false)

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

  const handleHistoryItemClick = (item: SearchHistoryItem) => {
    setUrl(item.url)
    setShowDropdown(false)
    onSubmit(item.url)
  }

  const formatTimeAgo = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
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
        <div className="flex-1 relative" ref={dropdownRef}>
          <label htmlFor="url-input" className="sr-only">
            Article URL
          </label>
          <div className="relative flex items-center">
            <input
              ref={inputRef}
              id="url-input"
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onFocus={() => history.length > 0 && setShowDropdown(true)}
              placeholder="Paste article URL here..."
              disabled={disabled}
              className={`${inputClasses} pr-10`}
            />
            {/* Source Info Popover */}
            <div className="absolute right-2 top-1/2 -translate-y-1/2">
              {sourceData && (
                <SourceInfoPopover
                  supported={sourceData.supported}
                  partial={sourceData.partial}
                  blocked={sourceData.blocked}
                />
              )}
            </div>
          </div>

          {/* Search History Dropdown */}
          {showDropdown && history.length > 0 && (
            <div className="absolute z-50 top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg max-h-80 overflow-y-auto">
              <div className="flex items-center justify-between px-3 py-2 border-b border-gray-100 dark:border-gray-700">
                <span className="text-xs font-medium text-gray-500 dark:text-gray-400">
                  Recent Searches
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation()
                    clearHistory()
                    setShowDropdown(false)
                  }}
                  className="text-xs text-gray-400 hover:text-red-500 dark:hover:text-red-400"
                >
                  Clear all
                </button>
              </div>
              <ul className="py-1">
                {history.map((item) => (
                  <li key={item.url + item.searchedAt}>
                    <button
                      type="button"
                      onClick={() => handleHistoryItemClick(item)}
                      className="w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700/50 flex items-start gap-3 group"
                    >
                      {/* Success/Failure Indicator */}
                      <span className="flex-shrink-0 mt-1">
                        {item.success ? (
                          <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                          </svg>
                        )}
                      </span>

                      {/* Article Info */}
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {item.title || 'Unknown Title'}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                          {item.source || new URL(item.url).hostname}
                        </div>
                        {!item.success && item.errorMessage && (
                          <div className="text-xs text-red-500 dark:text-red-400 truncate mt-0.5">
                            {item.errorMessage}
                          </div>
                        )}
                      </div>

                      {/* Time and Delete */}
                      <div className="flex-shrink-0 flex items-center gap-2">
                        <span className="text-xs text-gray-400">
                          {formatTimeAgo(item.searchedAt)}
                        </span>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation()
                            removeFromHistory(item.url)
                          }}
                          className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 dark:hover:text-red-400 p-1"
                        >
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

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

      {/* Example URLs - only fully supported sources */}
      <div className="mt-3 text-sm text-gray-500 dark:text-gray-400">
        <span>Try: </span>
        <button
          type="button"
          onClick={() => setUrl('https://www.bbc.com/news')}
          className="text-violet-600 hover:underline"
          disabled={disabled}
        >
          BBC
        </button>
        {' \u2022 '}
        <button
          type="button"
          onClick={() => setUrl('https://www.cnn.com/politics')}
          className="text-violet-600 hover:underline"
          disabled={disabled}
        >
          CNN
        </button>
        {' \u2022 '}
        <button
          type="button"
          onClick={() => setUrl('https://www.npr.org/sections/politics/')}
          className="text-violet-600 hover:underline"
          disabled={disabled}
        >
          NPR
        </button>
      </div>
    </form>
  )
}
