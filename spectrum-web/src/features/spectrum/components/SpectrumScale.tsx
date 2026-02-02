import { SpectrumLabels } from './SpectrumLabels'
import { SpectrumMarker } from './SpectrumMarker'

interface SpectrumScaleProps {
  score?: number
  confidence?: number
  showLabels?: boolean
  showAllLabels?: boolean
  height?: 'sm' | 'md' | 'lg'
  className?: string
}

export function SpectrumScale({
  score,
  confidence = 1,
  showLabels = true,
  showAllLabels = false,
  height = 'md',
  className = '',
}: SpectrumScaleProps) {
  const heightClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  }

  return (
    <div className={`w-full ${className}`}>
      {/* Scale track */}
      <div className="relative">
        <div
          className={`${heightClasses[height]} rounded-full overflow-hidden`}
          style={{
            background: `linear-gradient(to right, 
              #7c3aed 0%, 
              #8b5cf6 17%, 
              #a78bfa 33%, 
              #6b7280 50%, 
              #f59e0b 67%, 
              #f97316 83%, 
              #ea580c 100%
            )`,
          }}
        />

        {/* Marker */}
        {score !== undefined && (
          <div className="absolute inset-0 flex items-center">
            <SpectrumMarker
              score={score}
              confidence={confidence}
              showLabel={false}
              size={height}
            />
          </div>
        )}
      </div>

      {/* Labels */}
      {showLabels && <SpectrumLabels showAll={showAllLabels} />}
    </div>
  )
}
