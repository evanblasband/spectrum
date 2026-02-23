import type { RelatedArticlePreview } from '@/lib/api/client'
import { RelatedArticleCard } from './RelatedArticleCard'

interface RelatedArticlesListProps {
  articles: RelatedArticlePreview[]
  keywords: string[]
  onAnalyze?: (url: string) => void
  isLoading?: boolean
}

export function RelatedArticlesList({
  articles,
  keywords,
  onAnalyze,
  isLoading = false,
}: RelatedArticlesListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-24 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse"
          />
        ))}
      </div>
    )
  }

  if (articles.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500 dark:text-slate-400">
        No related articles found.
      </div>
    )
  }

  return (
    <div>
      {/* Keywords used for search */}
      {keywords.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          <span className="text-sm text-slate-500 dark:text-slate-400">
            Searched for:
          </span>
          {keywords.map((keyword) => (
            <span
              key={keyword}
              className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded text-xs"
            >
              {keyword}
            </span>
          ))}
        </div>
      )}

      {/* Article list */}
      <div className="space-y-3">
        {articles.map((article) => (
          <RelatedArticleCard
            key={article.url}
            article={article}
            onAnalyze={onAnalyze}
          />
        ))}
      </div>
    </div>
  )
}
