import { useState } from 'react'
import { UrlInputForm } from '@/features/analysis/components/UrlInputForm'
import { AnalysisCard } from '@/features/analysis/components/AnalysisCard'
import { useAnalyzeArticle } from '@/features/analysis/hooks/useAnalyzeArticle'
import { useFindRelated } from '@/features/related-articles/hooks/useFindRelated'
import { RelatedArticlesList } from '@/features/related-articles/components/RelatedArticlesList'
import { useComparisonStore } from '@/stores/useComparisonStore'
import { useSearchHistory } from '@/stores/useSearchHistory'
import { ComparisonView } from '@/features/comparison/components/ComparisonView'
import type { ArticleAnalysis } from '@/lib/api/client'

function App() {
  const [url, setUrl] = useState('')
  const [analyzedUrl, setAnalyzedUrl] = useState<string | null>(null)
  const { mutate: analyze, data, isPending, error, reset } = useAnalyzeArticle()
  const { data: relatedData, isLoading: relatedLoading } = useFindRelated(analyzedUrl)

  // Comparison state
  const { selectedArticles, addArticle, removeArticle, clearArticles } = useComparisonStore()
  const [showComparison, setShowComparison] = useState(false)

  // Search history
  const { addToHistory } = useSearchHistory()

  const handleAnalyze = (inputUrl: string) => {
    setUrl(inputUrl)
    setShowComparison(false)
    analyze(inputUrl, {
      onSuccess: (response) => {
        setAnalyzedUrl(inputUrl)
        // Add successful analysis to history
        addToHistory({
          url: inputUrl,
          title: response.data?.article_title || null,
          source: response.data?.source_name || null,
          success: true,
        })
      },
      onError: (err) => {
        // Add failed analysis to history
        addToHistory({
          url: inputUrl,
          title: null,
          source: null,
          success: false,
          errorMessage: err instanceof Error ? err.message : 'Analysis failed',
        })
      }
    })
  }

  const handleAnalyzeRelated = (relatedUrl: string) => {
    handleAnalyze(relatedUrl)
  }

  const handleAddToComparison = (analysis: ArticleAnalysis) => {
    addArticle(analysis)
  }

  const handleReset = () => {
    setUrl('')
    setAnalyzedUrl(null)
    setShowComparison(false)
    clearArticles()
    reset()
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Spectrum
          </h1>
          <p className="mt-1 text-gray-600 dark:text-gray-400">
            Understand where news articles fall on the political spectrum
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Input Form */}
        <div className="mb-8">
          <UrlInputForm
            onSubmit={handleAnalyze}
            isLoading={isPending}
            disabled={isPending}
          />
        </div>

        {/* Comparison Bar - shows when articles are selected */}
        {selectedArticles.length > 0 && !showComparison && (
          <div className="mb-8 p-4 bg-violet-50 dark:bg-violet-900/20 border border-violet-200 dark:border-violet-800 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-violet-700 dark:text-violet-300 font-medium">
                  {selectedArticles.length} article{selectedArticles.length > 1 ? 's' : ''} selected for comparison
                </span>
                <div className="text-sm text-violet-600 dark:text-violet-400 mt-1">
                  {selectedArticles.map(a => a.source_name).join(', ')}
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={clearArticles}
                  className="px-3 py-1 text-sm text-violet-600 dark:text-violet-400 hover:underline"
                >
                  Clear
                </button>
                {selectedArticles.length >= 2 && (
                  <button
                    onClick={() => setShowComparison(true)}
                    className="px-4 py-2 bg-violet-600 text-white rounded-lg hover:bg-violet-700 text-sm font-medium"
                  >
                    Compare Articles
                  </button>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Comparison View */}
        {showComparison && selectedArticles.length >= 2 && (
          <div className="mb-8">
            <button
              onClick={() => setShowComparison(false)}
              className="mb-4 text-sm text-violet-600 dark:text-violet-400 hover:underline"
            >
              &larr; Back to analysis
            </button>
            <ComparisonView
              articles={selectedArticles}
              consensusPoints={[]}
              contestedPoints={[]}
              overallSummary={generateComparisonSummary(selectedArticles)}
            />
          </div>
        )}

        {/* Error State */}
        {error && !showComparison && (
          <div className="mb-8 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-400">
              {error instanceof Error ? error.message : 'An error occurred'}
            </p>
            <button
              onClick={handleReset}
              className="mt-2 text-sm text-red-600 dark:text-red-400 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Loading State */}
        {isPending && !showComparison && (
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-400">
              Analyzing article...
            </p>
          </div>
        )}

        {/* Results */}
        {data?.data && !isPending && !showComparison && (
          <div className="space-y-8">
            {/* Analysis Card with Add to Comparison button */}
            <div>
              <div className="flex justify-end mb-2">
                {!useComparisonStore.getState().isSelected(data.data.article_id) ? (
                  <button
                    onClick={() => handleAddToComparison(data.data!)}
                    className="px-3 py-1 text-sm text-violet-600 dark:text-violet-400 border border-violet-300 dark:border-violet-700 rounded hover:bg-violet-50 dark:hover:bg-violet-900/20"
                  >
                    + Add to Comparison
                  </button>
                ) : (
                  <button
                    onClick={() => removeArticle(data.data!.article_id)}
                    className="px-3 py-1 text-sm text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-700 rounded"
                  >
                    Remove from Comparison
                  </button>
                )}
              </div>
              <AnalysisCard analysis={data.data} />
            </div>

            {/* Related Articles Section */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Related Articles
              </h3>
              {relatedLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-violet-600"></div>
                </div>
              ) : relatedData?.articles ? (
                <RelatedArticlesList
                  articles={relatedData.articles}
                  keywords={relatedData.original_keywords}
                  onAnalyze={handleAnalyzeRelated}
                />
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                  No related articles found. Make sure NEWSAPI_KEY is configured.
                </p>
              )}
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div className="mt-12 p-4 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm text-gray-600 dark:text-gray-400">
          <p>
            <strong>Disclaimer:</strong> This analysis is generated by AI and represents
            one interpretation of the article's content. Political spectrum placement is
            inherently subjective. Use this tool as one of many resources for media literacy.
          </p>
        </div>
      </main>
    </div>
  )
}

// Helper function to generate comparison summary
function generateComparisonSummary(articles: ArticleAnalysis[]): string {
  const scores = articles.map(a => a.political_leaning.score)
  const spread = Math.max(...scores) - Math.min(...scores)
  const sources = articles.map(a => a.source_name).join(', ')

  if (spread < 0.3) {
    return `The articles from ${sources} share similar political perspectives.`
  } else if (spread < 0.6) {
    return `The articles from ${sources} show moderate differences in political framing.`
  }
  return `The articles from ${sources} represent significantly different political viewpoints.`
}

export default App
