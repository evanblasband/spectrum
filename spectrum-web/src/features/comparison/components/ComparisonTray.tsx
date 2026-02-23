import { useState } from 'react'
import {
  useComparisonStore,
  isPendingArticle,
  getArticleId,
  type ComparisonArticle,
} from '@/stores/useComparisonStore'
import { getColor } from '@/features/spectrum/utils/spectrumColors'

interface ComparisonTrayProps {
  onCompare: () => void
  isComparing?: boolean
}

export function ComparisonTray({ onCompare, isComparing = false }: ComparisonTrayProps) {
  const { selectedArticles, removeArticle, clearArticles, hasPendingArticles } =
    useComparisonStore()
  const [isCollapsed, setIsCollapsed] = useState(false)

  if (selectedArticles.length === 0) {
    return null
  }

  const canCompare = selectedArticles.length >= 2
  const hasPending = hasPendingArticles()

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 transition-transform duration-300">
      {/* Collapse toggle */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -top-8 left-1/2 -translate-x-1/2 px-4 py-1 bg-slate-800 dark:bg-slate-700 text-white text-sm rounded-t-lg flex items-center gap-2 shadow-lg"
      >
        <span className="w-5 h-5 bg-blue-500 text-white rounded-full text-xs font-bold flex items-center justify-center">
          {selectedArticles.length}
        </span>
        <span>Comparison</span>
        <svg
          className={`w-4 h-4 transition-transform ${isCollapsed ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Tray content */}
      <div
        className={`bg-white dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700 shadow-2xl transition-all duration-300 ${
          isCollapsed ? 'h-0 overflow-hidden' : 'h-auto'
        }`}
      >
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            {/* Article cards */}
            <div className="flex-1 flex gap-3 overflow-x-auto pb-2">
              {selectedArticles.map((article) => (
                <ArticleCard
                  key={getArticleId(article)}
                  article={article}
                  onRemove={() => removeArticle(getArticleId(article))}
                />
              ))}

              {/* Add more placeholder */}
              {selectedArticles.length < 5 && (
                <div className="flex-shrink-0 w-40 h-20 border-2 border-dashed border-slate-300 dark:border-slate-600 rounded-lg flex items-center justify-center text-slate-400 dark:text-slate-500 text-sm">
                  + Add more
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="flex-shrink-0 flex flex-col gap-2">
              <button
                onClick={onCompare}
                disabled={!canCompare || isComparing}
                className={`px-6 py-2 rounded-lg font-medium text-sm transition-colors ${
                  canCompare && !isComparing
                    ? 'bg-slate-800 dark:bg-slate-700 text-white hover:bg-slate-900 dark:hover:bg-slate-600'
                    : 'bg-slate-200 dark:bg-slate-700 text-slate-400 cursor-not-allowed'
                }`}
              >
                {isComparing ? (
                  <span className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Comparing...
                  </span>
                ) : (
                  `Compare ${selectedArticles.length} Articles`
                )}
              </button>

              {hasPending && !isComparing && (
                <p className="text-xs text-amber-600 dark:text-amber-400 text-center">
                  Some articles will be analyzed
                </p>
              )}

              <button
                onClick={clearArticles}
                className="text-sm text-slate-500 hover:text-red-500 dark:hover:text-red-400"
              >
                Clear all
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function ArticleCard({
  article,
  onRemove,
}: {
  article: ComparisonArticle
  onRemove: () => void
}) {
  const isPending = isPendingArticle(article)
  const source = isPending ? article.source : article.source_name
  const title = isPending ? article.title : article.article_title
  const score = isPending ? null : article.political_leaning.score
  const color = score !== null ? getColor(score) : '#94a3b8'

  return (
    <div
      className="relative flex-shrink-0 w-44 p-3 bg-slate-50 dark:bg-slate-700/50 rounded-lg border border-slate-200 dark:border-slate-600 group"
      style={{ borderLeftColor: color, borderLeftWidth: '3px' }}
    >
      {/* Remove button */}
      <button
        onClick={onRemove}
        className="absolute -top-2 -right-2 w-5 h-5 bg-slate-200 dark:bg-slate-600 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-500 hover:text-white"
      >
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>

      {/* Pending indicator */}
      {isPending && (
        <div className="absolute top-1 right-1 px-1.5 py-0.5 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 text-[10px] rounded">
          Pending
        </div>
      )}

      {/* Content */}
      <div className="text-xs font-medium text-slate-900 dark:text-white truncate">
        {source}
      </div>
      <div className="text-[11px] text-slate-500 dark:text-slate-400 line-clamp-2 mt-1">
        {title}
      </div>

      {/* Score indicator */}
      {score !== null && (
        <div className="mt-2 flex items-center gap-1">
          <div className="flex-1 h-1 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
            <div
              className="h-full rounded-full"
              style={{
                width: `${((score + 1) / 2) * 100}%`,
                backgroundColor: color,
              }}
            />
          </div>
          <span className="text-[10px] text-slate-400">
            {score > 0 ? '+' : ''}{score.toFixed(1)}
          </span>
        </div>
      )}
    </div>
  )
}
