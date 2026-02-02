import { getColor, getLabel, scoreToPercent } from '../utils/spectrumColors'

interface SpectrumMarkerProps {
  score: number
  confidence?: number
  showLabel?: boolean
  size?: 'sm' | 'md' | 'lg'
}

export function SpectrumMarker({
  score,
  confidence = 1,
  showLabel = true,
  size = 'md',
}: SpectrumMarkerProps) {
  const percent = scoreToPercent(score)
  const color = getColor(score)
  const label = getLabel(score)

  const sizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
  }

  // Confidence affects opacity
  const opacity = 0.5 + confidence * 0.5

  return (
    <div
      className="absolute transform -translate-x-1/2 flex flex-col items-center"
      style={{ left: `${percent}%` }}
    >
      {/* Marker dot */}
      <div
        className={`${sizeClasses[size]} rounded-full border-2 border-white dark:border-gray-800 shadow-md`}
        style={{ backgroundColor: color, opacity }}
      />
      
      {/* Label */}
      {showLabel && (
        <div className="mt-2 text-xs font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
          {label}
          <span className="ml-1 text-gray-500">
            ({score > 0 ? '+' : ''}{score.toFixed(2)})
          </span>
        </div>
      )}
    </div>
  )
}
