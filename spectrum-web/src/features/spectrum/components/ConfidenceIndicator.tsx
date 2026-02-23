import { useState } from 'react'

interface ConfidenceIndicatorProps {
  confidence: number // 0 to 1
  showLabel?: boolean
  showInfoIcon?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function ConfidenceIndicator({
  confidence,
  showLabel = true,
  showInfoIcon = true,
  size = 'md',
}: ConfidenceIndicatorProps) {
  const [showTooltip, setShowTooltip] = useState(false)
  const percentage = Math.round(confidence * 100)

  // Color based on confidence level
  const getConfidenceColor = () => {
    if (confidence >= 0.8) return 'bg-green-500'
    if (confidence >= 0.6) return 'bg-yellow-500'
    return 'bg-orange-500'
  }

  const sizeClasses = {
    sm: 'h-1 w-16',
    md: 'h-2 w-24',
    lg: 'h-3 w-32',
  }

  const textSizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
  }

  const colorClass = getConfidenceColor()

  return (
    <div className="flex items-center gap-2">
      {showLabel && (
        <span className={textSizes[size] + ' text-slate-600 dark:text-slate-400'}>
          Confidence:
        </span>
      )}
      <div className={sizeClasses[size] + ' bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden'}>
        <div
          className={'h-full rounded-full transition-all ' + colorClass}
          style={{ width: percentage + '%' }}
        />
      </div>
      <span className={textSizes[size] + ' font-medium text-slate-700 dark:text-slate-300'}>
        {percentage}%
      </span>

      {/* Info Icon with Tooltip */}
      {showInfoIcon && (
        <div className="relative">
          <button
            type="button"
            className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 focus:outline-none"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            onFocus={() => setShowTooltip(true)}
            onBlur={() => setShowTooltip(false)}
            aria-label="Confidence information"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </button>

          {/* Tooltip */}
          {showTooltip && (
            <div className="absolute z-50 bottom-full right-0 mb-2 w-64 p-3 bg-gray-900 text-white text-xs rounded-lg shadow-lg">
              <p className="font-medium mb-1">What is Confidence?</p>
              <p className="text-gray-300 mb-2">
                Confidence indicates how certain the AI is about its political leaning assessment.
              </p>
              <p className="font-medium mb-1">How it's determined:</p>
              <ul className="text-gray-300 space-y-1">
                <li>• Clarity of political framing in the text</li>
                <li>• Consistency of language patterns</li>
                <li>• Presence of explicit policy positions</li>
                <li>• Amount of analyzable content</li>
              </ul>
              <p className="text-gray-400 mt-2 text-[10px]">
                Higher confidence = more reliable score
              </p>
              {/* Tooltip arrow */}
              <div className="absolute top-full right-4 border-4 border-transparent border-t-gray-900" />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
