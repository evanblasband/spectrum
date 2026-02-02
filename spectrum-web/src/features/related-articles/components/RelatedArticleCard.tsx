import type { RelatedArticlePreview } from '@/lib/api/client'

interface RelatedArticleCardProps {
  article: RelatedArticlePreview
  onAnalyze?: (url: string) => void
}

export function RelatedArticleCard({ article, onAnalyze }: RelatedArticleCardProps) {
  const formattedDate = article.published_at
    ? new Date(article.published_at).toLocaleDateString()
    : null

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
        {onAnalyze && (
          <button
            onClick={() => onAnalyze(article.url)}
            className="flex-shrink-0 px-3 py-1 text-xs font-medium text-violet-600 dark:text-violet-400 border border-violet-300 dark:border-violet-700 rounded hover:bg-violet-50 dark:hover:bg-violet-900/20 transition-colors"
          >
            Analyze
          </button>
        )}
      </div>
    </div>
  )
}
