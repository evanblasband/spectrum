import type { ArticleAnalysis } from '@/lib/api/client'
import { ComparisonSpectrum } from './ComparisonSpectrum'
import { ComparisonSummary } from './ComparisonSummary'
import { getLabel } from '@/features/spectrum/utils/spectrumColors'

interface ComparisonViewProps {
  articles: ArticleAnalysis[]
  consensusPoints: string[]
  contestedPoints: string[]
  overallSummary: string
}

export function ComparisonView({
  articles,
  consensusPoints,
  contestedPoints,
  overallSummary,
}: ComparisonViewProps) {
  // Calculate spread
  const scores = articles.map((a) => a.political_leaning.score)
  const leaningSpread = Math.max(...scores) - Math.min(...scores)

  // Find common topics
  const topicSets = articles.map(
    (a) => new Set([a.topics.primary_topic, ...a.topics.secondary_topics])
  )
  const commonTopics = Array.from(
    topicSets.reduce((acc, set) => {
      if (acc.size === 0) return set
      return new Set([...acc].filter((topic) => set.has(topic)))
    }, new Set<string>())
  )

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-100 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          Comparison: {articles.length} Articles
        </h2>
        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
          Comparing coverage from {articles.map((a) => a.source_name).join(', ')}
        </p>
      </div>

      {/* Spectrum Visualization */}
      <div className="p-6 bg-gray-50 dark:bg-gray-900/50">
        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
          Political Spectrum Positions
        </h3>
        <ComparisonSpectrum articles={articles} />

        {/* Legend */}
        <div className="mt-8 flex flex-wrap gap-4">
          {articles.map((article) => (
            <div
              key={article.article_id}
              className="flex items-center gap-2 text-sm"
            >
              <div
                className="w-3 h-3 rounded-full"
                style={{
                  backgroundColor:
                    article.political_leaning.score <= -0.3
                      ? '#8b5cf6'
                      : article.political_leaning.score >= 0.3
                      ? '#f97316'
                      : '#6b7280',
                }}
              />
              <span className="text-gray-700 dark:text-gray-300">
                {article.source_name}
              </span>
              <span className="text-gray-500">
                ({getLabel(article.political_leaning.score)})
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Summary */}
      <div className="p-6">
        <ComparisonSummary
          leaningSpread={leaningSpread}
          commonTopics={commonTopics}
          agreements={consensusPoints}
          disagreements={contestedPoints}
          overallSummary={overallSummary}
        />
      </div>
    </div>
  )
}
