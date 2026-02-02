/**
 * Labels for the political spectrum scale
 */

interface SpectrumLabelsProps {
  showAll?: boolean
}

export function SpectrumLabels({ showAll = false }: SpectrumLabelsProps) {
  const labels = showAll
    ? [
        { label: 'Far Left', position: 0 },
        { label: 'Left', position: 17 },
        { label: 'Slight Left', position: 33 },
        { label: 'Center', position: 50 },
        { label: 'Slight Right', position: 67 },
        { label: 'Right', position: 83 },
        { label: 'Far Right', position: 100 },
      ]
    : [
        { label: 'Left', position: 0 },
        { label: 'Center', position: 50 },
        { label: 'Right', position: 100 },
      ]

  return (
    <div className="relative h-6 mt-2">
      {labels.map(({ label, position }) => (
        <span
          key={label}
          className="absolute text-xs text-gray-500 dark:text-gray-400 transform -translate-x-1/2"
          style={{ left: `${position}%` }}
        >
          {label}
        </span>
      ))}
    </div>
  )
}
