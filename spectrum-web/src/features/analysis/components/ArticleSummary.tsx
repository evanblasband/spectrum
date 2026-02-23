import type { ArticleAnalysis } from '@/lib/api/client'

interface ArticleSummaryProps {
  analysis: ArticleAnalysis
}

export function ArticleSummary({ analysis }: ArticleSummaryProps) {
  const { topics, key_points } = analysis

  const getSentimentColor = (sentiment: string) => {
    if (sentiment === 'positive') return 'bg-green-500'
    if (sentiment === 'negative') return 'bg-red-500'
    return 'bg-slate-400'
  }

  return (
    <div className="space-y-4">
      {/* Topics */}
      <div>
        <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
          Topics
        </h4>
        <div className="flex flex-wrap gap-2">
          <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-sm font-medium">
            {topics.primary_topic}
          </span>
          {topics.secondary_topics.map((topic) => (
            <span
              key={topic}
              className="px-3 py-1 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded-full text-sm"
            >
              {topic}
            </span>
          ))}
        </div>
      </div>

      {/* Keywords */}
      {topics.keywords.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Keywords
          </h4>
          <div className="flex flex-wrap gap-1">
            {topics.keywords.map((keyword) => (
              <span
                key={keyword}
                className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-500 dark:text-slate-400 rounded text-xs"
              >
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Key Points */}
      {key_points.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
            Key Points
          </h4>
          <ul className="space-y-2">
            {key_points.map((point) => (
              <li key={point.id} className="flex gap-2 text-sm">
                <span
                  className={'flex-shrink-0 w-2 h-2 mt-1.5 rounded-full ' + getSentimentColor(point.sentiment)}
                />
                <span className="text-slate-700 dark:text-slate-300">
                  {point.statement}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
