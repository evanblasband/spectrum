import { useState } from 'react'
import { UrlInputForm } from '@/features/analysis/components/UrlInputForm'
import { AnalysisCard } from '@/features/analysis/components/AnalysisCard'
import { useAnalyzeArticle } from '@/features/analysis/hooks/useAnalyzeArticle'
import { useFindRelated } from '@/features/related-articles/hooks/useFindRelated'
import { RelatedArticlesList } from '@/features/related-articles/components/RelatedArticlesList'
import { useComparisonStore, isPendingArticle } from '@/stores/useComparisonStore'
import { useSearchHistory } from '@/stores/useSearchHistory'
import { ComparisonView } from '@/features/comparison/components/ComparisonView'
import { ComparisonTray } from '@/features/comparison/components/ComparisonTray'
import { useCompareArticles } from '@/features/comparison/hooks/useCompareArticles'
import { ErrorMessage } from '@/components/common/ErrorMessage'
import type { ArticleAnalysis } from '@/lib/api/client'

function App() {
  const [url, setUrl] = useState('')
  const [analyzedUrl, setAnalyzedUrl] = useState<string | null>(null)
  const { mutate: analyze, data, isPending, error } = useAnalyzeArticle()
  const { data: relatedData, isLoading: relatedLoading } = useFindRelated(analyzedUrl)

  // Comparison state
  const { selectedArticles, addArticle, removeArticle } = useComparisonStore()
  const [showComparison, setShowComparison] = useState(false)
  const {
    mutate: compare,
    data: comparisonData,
    isPending: isComparing,
    error: comparisonError,
    reset: resetComparison,
  } = useCompareArticles()

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

  const handleRetry = () => {
    if (url) {
      handleAnalyze(url)
    }
  }

  const handleCompare = () => {
    // Get URLs from all articles (both analyzed and pending)
    const urls = selectedArticles.map((article) => {
      if (isPendingArticle(article)) {
        return article.url
      }
      return article.article_url
    })

    setShowComparison(true)
    compare({ urls })
  }

  const hasArticlesInTray = selectedArticles.length > 0

  return (
    <div className={`min-h-screen bg-gray-50 dark:bg-gray-900 ${hasArticlesInTray ? 'pb-32' : ''}`}>
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
            value={url}
            onChange={setUrl}
          />
        </div>

        {/* Comparison View */}
        {showComparison && (
          <div className="mb-8">
            <button
              onClick={() => {
                setShowComparison(false)
                resetComparison()
              }}
              className="mb-4 text-sm text-violet-600 dark:text-violet-400 hover:underline"
            >
              &larr; Back to analysis
            </button>

            {/* Comparison Loading */}
            {isComparing && (
              <div className="flex flex-col items-center justify-center py-12 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-violet-600"></div>
                <p className="mt-4 text-gray-600 dark:text-gray-400">
                  Analyzing and comparing articles...
                </p>
              </div>
            )}

            {/* Comparison Error */}
            {comparisonError && !isComparing && (
              <ErrorMessage
                error={comparisonError}
                onRetry={handleCompare}
              />
            )}

            {/* Comparison Results */}
            {comparisonData && !isComparing && (
              <ComparisonView
                articles={comparisonData.articles}
                pairwiseComparisons={comparisonData.pairwise_comparisons}
                consensusPoints={comparisonData.consensus_points}
                contestedPoints={comparisonData.contested_points}
                overallSummary={comparisonData.overall_summary}
              />
            )}
          </div>
        )}

        {/* Error State */}
        {error && !showComparison && (
          <ErrorMessage
            error={error}
            onRetry={handleRetry}
            className="mb-8"
          />
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
                    className="px-3 py-1 text-sm text-violet-600 dark:text-violet-400 border border-violet-300 dark:border-violet-700 rounded hover:bg-violet-50 dark:hover:bg-violet-900/20 flex items-center gap-1"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    Add to Comparison
                  </button>
                ) : (
                  <button
                    onClick={() => removeArticle(data.data!.article_id)}
                    className="px-3 py-1 text-sm bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 border border-violet-300 dark:border-violet-700 rounded flex items-center gap-1"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    In Comparison
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

      {/* Comparison Tray */}
      {!showComparison && (
        <ComparisonTray onCompare={handleCompare} isComparing={isComparing} />
      )}
    </div>
  )
}

export default App
