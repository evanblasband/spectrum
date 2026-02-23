export type DetailLevel = 'summary' | 'side-by-side' | 'diff'

interface DetailLevelToggleProps {
  level: DetailLevel
  onChange: (level: DetailLevel) => void
}

const LEVELS: { value: DetailLevel; label: string; description: string }[] = [
  { value: 'summary', label: 'Summary', description: 'Key points overview' },
  { value: 'side-by-side', label: 'Side-by-Side', description: 'Compare arguments' },
  { value: 'diff', label: 'Detailed', description: 'Topic-by-topic breakdown' },
]

export function DetailLevelToggle({ level, onChange }: DetailLevelToggleProps) {
  return (
    <div className="inline-flex rounded-lg bg-slate-100 dark:bg-slate-700 p-1">
      {LEVELS.map((option) => (
        <button
          key={option.value}
          onClick={() => onChange(option.value)}
          className={`
            px-4 py-2 text-sm font-medium rounded-md transition-colors
            ${
              level === option.value
                ? 'bg-white dark:bg-slate-600 text-slate-900 dark:text-white shadow-sm'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
            }
          `}
          title={option.description}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
