interface ComparisonSummaryProps {
  leaningSpread: number
  commonTopics: string[]
  agreements: string[]
  disagreements: string[]
  overallSummary: string
}

export function ComparisonSummary({
  leaningSpread,
  commonTopics,
  agreements,
  disagreements,
  overallSummary,
}: ComparisonSummaryProps) {
  const spreadLabel =
    leaningSpread < 0.3
      ? 'Low'
      : leaningSpread < 0.6
      ? 'Moderate'
      : 'High'

  const spreadColor =
    leaningSpread < 0.3
      ? 'text-green-600 dark:text-green-400'
      : leaningSpread < 0.6
      ? 'text-yellow-600 dark:text-yellow-400'
      : 'text-red-600 dark:text-red-400'

  return (
    <div className="space-y-6">
      {/* Overall Summary */}
      <div className="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
        <p className="text-gray-700 dark:text-gray-300">{overallSummary}</p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Political Spread
          </div>
          <div className={'text-2xl font-bold ' + spreadColor}>
            {spreadLabel}
          </div>
          <div className="text-xs text-gray-400">
            Difference: {leaningSpread.toFixed(2)}
          </div>
        </div>

        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Agreements
          </div>
          <div className="text-2xl font-bold text-green-600 dark:text-green-400">
            {agreements.length}
          </div>
        </div>

        <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            Disagreements
          </div>
          <div className="text-2xl font-bold text-orange-600 dark:text-orange-400">
            {disagreements.length}
          </div>
        </div>
      </div>

      {/* Common Topics */}
      {commonTopics.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Shared Topics
          </h4>
          <div className="flex flex-wrap gap-2">
            {commonTopics.map((topic) => (
              <span
                key={topic}
                className="px-3 py-1 bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 rounded-full text-sm"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Agreements */}
      {agreements.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Key Agreements
          </h4>
          <ul className="space-y-2">
            {agreements.map((agreement, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-green-500">+</span>
                <span className="text-gray-700 dark:text-gray-300">
                  {agreement}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Disagreements */}
      {disagreements.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Key Disagreements
          </h4>
          <ul className="space-y-2">
            {disagreements.map((disagreement, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-orange-500">-</span>
                <span className="text-gray-700 dark:text-gray-300">
                  {disagreement}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
