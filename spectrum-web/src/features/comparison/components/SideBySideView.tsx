import type { ArticleAnalysis, ArticleComparisonPair } from '@/lib/api/client'
import { getLabel, getColor } from '@/features/spectrum/utils/spectrumColors'

interface SideBySideViewProps {
  articles: ArticleAnalysis[]
  pairwiseComparisons: ArticleComparisonPair[]
}

export function SideBySideView({ articles, pairwiseComparisons }: SideBySideViewProps) {
  // For now, show first two articles side by side
  const [articleA, articleB] = articles.slice(0, 2)

  // Find the comparison pair for these two articles
  const comparison = pairwiseComparisons.find(
    (p) =>
      (p.article_a_id === articleA?.article_id && p.article_b_id === articleB?.article_id) ||
      (p.article_a_id === articleB?.article_id && p.article_b_id === articleA?.article_id)
  )

  if (!articleA || !articleB) {
    return <div className="text-gray-500">Need at least 2 articles for side-by-side comparison</div>
  }

  return (
    <div className="space-y-6">
      {/* Article Headers */}
      <div className="grid grid-cols-2 gap-4">
        <ArticleHeader article={articleA} />
        <ArticleHeader article={articleB} />
      </div>

      {/* Key Points Comparison */}
      <div className="grid grid-cols-2 gap-4">
        <KeyPointsSection article={articleA} label="Key Arguments" />
        <KeyPointsSection article={articleB} label="Key Arguments" />
      </div>

      {/* Topics */}
      <div className="grid grid-cols-2 gap-4">
        <TopicsSection article={articleA} comparison={comparison} isArticleA={true} />
        <TopicsSection article={articleB} comparison={comparison} isArticleA={false} />
      </div>

      {/* Entities/Sources */}
      <div className="grid grid-cols-2 gap-4">
        <EntitiesSection article={articleA} />
        <EntitiesSection article={articleB} />
      </div>
    </div>
  )
}

function ArticleHeader({ article }: { article: ArticleAnalysis }) {
  const score = article.political_leaning.score
  const color = getColor(score)

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 dark:text-white truncate">
            {article.source_name}
          </h3>
          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mt-1">
            {article.article_title}
          </p>
        </div>
        <div
          className="flex-shrink-0 px-2 py-1 rounded text-xs font-medium"
          style={{ backgroundColor: `${color}20`, color }}
        >
          {getLabel(score)}
        </div>
      </div>
      <div className="mt-3 flex items-center gap-2">
        <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all"
            style={{
              width: `${((score + 1) / 2) * 100}%`,
              backgroundColor: color,
            }}
          />
        </div>
        <span className="text-xs text-gray-500 w-12 text-right">
          {score > 0 ? '+' : ''}{score.toFixed(2)}
        </span>
      </div>
    </div>
  )
}

function KeyPointsSection({ article, label }: { article: ArticleAnalysis; label: string }) {
  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">{label}</h4>
      {article.key_points.length > 0 ? (
        <ul className="space-y-3">
          {article.key_points.map((point) => (
            <li key={point.id} className="text-sm">
              <div className="flex items-start gap-2">
                <span
                  className={`flex-shrink-0 mt-1 w-2 h-2 rounded-full ${
                    point.sentiment === 'positive'
                      ? 'bg-green-500'
                      : point.sentiment === 'negative'
                      ? 'bg-red-500'
                      : 'bg-gray-400'
                  }`}
                />
                <div>
                  <p className="text-gray-700 dark:text-gray-300">{point.statement}</p>
                  {point.supporting_quote && (
                    <p className="mt-1 text-xs text-gray-500 dark:text-gray-500 italic">
                      "{point.supporting_quote}"
                    </p>
                  )}
                </div>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-gray-500">No key points extracted</p>
      )}
    </div>
  )
}

function TopicsSection({
  article,
  comparison,
  isArticleA,
}: {
  article: ArticleAnalysis
  comparison?: ArticleComparisonPair
  isArticleA: boolean
}) {
  const sharedTopics = comparison?.shared_topics || []
  const uniqueTopics = isArticleA
    ? comparison?.unique_topics_a || []
    : comparison?.unique_topics_b || []

  const allTopics = [article.topics.primary_topic, ...article.topics.secondary_topics]

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Topics</h4>
      <div className="flex flex-wrap gap-1.5">
        {allTopics.map((topic) => {
          const isShared = sharedTopics.includes(topic)
          const isUnique = uniqueTopics.includes(topic)
          return (
            <span
              key={topic}
              className={`px-2 py-0.5 text-xs rounded ${
                isShared
                  ? 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300'
                  : isUnique
                  ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
              }`}
              title={isShared ? 'Shared topic' : isUnique ? 'Unique to this article' : ''}
            >
              {topic}
            </span>
          )
        })}
      </div>
      <div className="mt-2 flex gap-3 text-xs text-gray-500">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-violet-500" /> Shared
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded bg-amber-500" /> Unique
        </span>
      </div>
    </div>
  )
}

function EntitiesSection({ article }: { article: ArticleAnalysis }) {
  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        People & Organizations Mentioned
      </h4>
      {article.topics.entities.length > 0 ? (
        <div className="flex flex-wrap gap-1.5">
          {article.topics.entities.map((entity) => (
            <span
              key={entity}
              className="px-2 py-0.5 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded"
            >
              {entity}
            </span>
          ))}
        </div>
      ) : (
        <p className="text-sm text-gray-500">No entities extracted</p>
      )}
    </div>
  )
}
