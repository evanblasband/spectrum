interface ConfidenceIndicatorProps {
  confidence: number // 0 to 1
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function ConfidenceIndicator({
  confidence,
  showLabel = true,
  size = 'md',
}: ConfidenceIndicatorProps) {
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
        <span className={textSizes[size] + ' text-gray-600 dark:text-gray-400'}>
          Confidence:
        </span>
      )}
      <div className={sizeClasses[size] + ' bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden'}>
        <div
          className={'h-full rounded-full transition-all ' + colorClass}
          style={{ width: percentage + '%' }}
        />
      </div>
      <span className={textSizes[size] + ' font-medium text-gray-700 dark:text-gray-300'}>
        {percentage}%
      </span>
    </div>
  )
}
