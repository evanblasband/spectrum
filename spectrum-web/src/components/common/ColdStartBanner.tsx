import { useBackendStatus } from '@/hooks/useBackendStatus'

export function ColdStartBanner() {
  const { status, elapsedSeconds, checkStatus } = useBackendStatus()

  // Don't show anything if backend is awake
  if (status === 'awake') {
    return null
  }

  // Initial check - show nothing to avoid flash
  if (status === 'checking') {
    return null
  }

  // Error state
  if (status === 'error') {
    return (
      <div className="bg-red-50 dark:bg-red-900 border-b border-red-200 dark:border-red-800">
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <p className="text-sm text-red-700 dark:text-red-300">
                Unable to connect to the server. It may be temporarily unavailable.
              </p>
            </div>
            <button
              onClick={checkStatus}
              className="text-sm font-medium text-red-700 dark:text-red-300 hover:text-red-800 dark:hover:text-red-200 underline"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  // Waking state - friendly cold start message
  return (
    <div className="bg-blue-50 dark:bg-blue-900 border-b border-blue-200 dark:border-blue-800">
      <div className="max-w-6xl mx-auto px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex-shrink-0">
            <svg className="animate-spin h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          </div>
          <div className="flex-1">
            <p className="text-sm text-blue-700 dark:text-blue-300">
              <span className="font-medium">Waking up the server...</span>
              {' '}This app runs on a free tier that sleeps after inactivity.
              {elapsedSeconds > 0 && (
                <span className="text-blue-600 dark:text-blue-400">
                  {' '}({elapsedSeconds}s)
                </span>
              )}
            </p>
            {elapsedSeconds > 15 && (
              <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
                Almost there! Cold starts typically take 20-40 seconds.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
