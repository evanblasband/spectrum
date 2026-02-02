import { getColor } from '../utils/spectrumColors'

interface MiniSpectrumProps {
  score: number
  size?: 'sm' | 'md'
}

export function MiniSpectrum({ score, size = 'sm' }: MiniSpectrumProps) {
  const color = getColor(score)
  const percent = ((score + 1) / 2) * 100

  const heights = {
    sm: 'h-1',
    md: 'h-2',
  }

  return (
    <div className={'w-full rounded-full overflow-hidden relative ' + heights[size]}
      style={{
        background: 'linear-gradient(to right, #7c3aed, #6b7280, #ea580c)',
      }}
    >
      {/* Marker */}
      <div
        className="absolute top-0 h-full w-1 -ml-0.5"
        style={{
          left: percent + '%',
          backgroundColor: color,
          boxShadow: '0 0 4px rgba(0,0,0,0.3)',
        }}
      />
    </div>
  )
}
