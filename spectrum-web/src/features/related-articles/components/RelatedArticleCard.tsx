import type { RelatedArticlePreview } from '@/lib/api/client'
import { useComparisonStore } from '@/stores/useComparisonStore'

interface RelatedArticleCardProps {
  article: RelatedArticlePreview
  onAnalyze?: (url: string) => void
}

export function RelatedArticleCard({ article, onAnalyze }: RelatedArticleCardProps) {
  const { addPendingArticle, removeArticle, isSelected } = useComparisonStore()
  const isInComparison = isSelected(article.url)

  const formattedDate = article.published_at
    ? new Date(article.published_at).toLocaleDateString()
    : null

  const handleToggleCompare = () => {
    if (isInComparison) {
      removeArticle(article.url)
    } else {
      addPendingArticle(article)
    }
  }

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-violet-300 dark:hover:border-violet-700 transition-colors">
      <div className="flex justify-between items-start gap-3">
        <div className="flex-1 min-w-0">
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-gray-900 dark:text-white hover:text-violet-600 dark:hover:text-violet-400 line-clamp-2"
          >
            {article.title}
          </a>
          <div className="mt-1 flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
            <span className="font-medium">{article.source}</span>
            {formattedDate && (
              <>
                <span>&bull;</span>
                <span>{formattedDate}</span>
              </>
            )}
          </div>
          {article.snippet && (
            <p className="mt-2 text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
              {article.snippet}
            </p>
          )}
        </div>

        {/* Action buttons */}
        <div className="flex-shrink-0 flex flex-col gap-2">
          {onAnalyze && (
            <button
              onClick={() => onAnalyze(article.url)}
              className="px-3 py-1 text-xs font-medium text-violet-600 dark:text-violet-400 border border-violet-300 dark:border-violet-700 rounded hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors"
            >
              Analyze
            </button>
          )}
          <button
            onClick={handleToggleCompare}
            className={`px-3 py-1 text-xs font-medium rounded transition-colors flex items-center gap-1 ${
              isInComparison
                ? 'bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 border border-violet-300 dark:border-violet-700'
                : 'text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 hover:border-violet-300 dark:hover:border-violet-600'
            }`}
          >
            {isInComparison ? (
              <>
                <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Added
              </>
            ) : (
              <>
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Compare
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
