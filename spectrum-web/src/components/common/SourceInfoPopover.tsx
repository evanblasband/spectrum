import { useState, useRef, useEffect } from 'react'

interface BlockedSource {
  domain: string
  reason: string
}

interface SourceInfoPopoverProps {
  supported: string[]
  blocked: BlockedSource[]
}

export function SourceInfoPopover({ supported, blocked }: SourceInfoPopoverProps) {
  const [isOpen, setIsOpen] = useState(false)
  const popoverRef = useRef<HTMLDivElement>(null)
  const buttonRef = useRef<HTMLButtonElement>(null)

  // Close popover when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        popoverRef.current &&
        !popoverRef.current.contains(event.target as Node) &&
        buttonRef.current &&
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Close on escape key
  useEffect(() => {
    function handleEscape(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        setIsOpen(false)
      }
    }
    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [])

  // Map domains to proper display names
  const DOMAIN_NAMES: Record<string, string> = {
    // Left-leaning
    'npr.org': 'NPR',
    'theguardian.com': 'The Guardian',
    'huffpost.com': 'HuffPost',
    'vox.com': 'Vox',
    'motherjones.com': 'Mother Jones',
    'slate.com': 'Slate',
    'theatlantic.com': 'The Atlantic',
    'msnbc.com': 'MSNBC',
    // Center
    'apnews.com': 'AP News',
    'bbc.com': 'BBC',
    'bbc.co.uk': 'BBC',
    'pbs.org': 'PBS',
    'usatoday.com': 'USA Today',
    'abcnews.go.com': 'ABC News',
    'cbsnews.com': 'CBS News',
    'nbcnews.com': 'NBC News',
    // Right-leaning
    'foxnews.com': 'Fox News',
    'nationalreview.com': 'National Review',
    'breitbart.com': 'Breitbart',
    'nypost.com': 'NY Post',
    'washingtonexaminer.com': 'Washington Examiner',
    'dailywire.com': 'Daily Wire',
    // Major papers
    'nytimes.com': 'NY Times',
    'latimes.com': 'LA Times',
    'chicagotribune.com': 'Chicago Tribune',
    'cnn.com': 'CNN',
    // Blocked sites
    'washingtonpost.com': 'Washington Post',
    'wsj.com': 'Wall Street Journal',
    'reuters.com': 'Reuters',
    'politico.com': 'Politico',
    'thehill.com': 'The Hill',
    'thefederalist.com': 'The Federalist',
  }

  const formatDomain = (domain: string): string => {
    return DOMAIN_NAMES[domain] || domain
  }

  return (
    <div className="relative inline-block">
      <button
        ref={buttonRef}
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-violet-500 rounded-full"
        aria-label="View supported news sources"
        aria-expanded={isOpen}
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
      </button>

      {isOpen && (
        <div
          ref={popoverRef}
          className="absolute z-50 right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 overflow-hidden"
          role="dialog"
          aria-label="Supported news sources"
        >
          {/* Header */}
          <div className="px-4 py-3 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
              News Source Compatibility
            </h3>
          </div>

          <div className="max-h-80 overflow-y-auto">
            {/* Supported Sources */}
            <div className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  Supported Sources ({supported.length})
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {supported.map((domain) => (
                  <span
                    key={domain}
                    className="inline-block px-2 py-0.5 text-xs bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded"
                  >
                    {formatDomain(domain)}
                  </span>
                ))}
              </div>
            </div>

            {/* Divider */}
            <div className="border-t border-gray-200 dark:border-gray-700" />

            {/* Blocked Sources */}
            <div className="p-4">
              <div className="flex items-center gap-2 mb-2">
                <svg className="w-4 h-4 text-amber-500" fill="currentColor" viewBox="0 0 20 20">
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  Known Issues ({blocked.length})
                </span>
              </div>
              <div className="space-y-1.5">
                {blocked.map(({ domain, reason }) => (
                  <div key={domain} className="text-xs text-gray-600 dark:text-gray-400">
                    <span className="font-medium text-amber-700 dark:text-amber-400">
                      {formatDomain(domain)}
                    </span>
                  </div>
                ))}
              </div>
              <p className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                These sites block automated access or require subscriptions.
              </p>
            </div>
          </div>

          {/* Footer */}
          <div className="px-4 py-2 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Most major news sources work. Blocked sites have anti-bot protection.
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
