import type { ArticleAnalysis } from '@/lib/api/client'
import { SpectrumScale } from '@/features/spectrum/components/SpectrumScale'
import { ConfidenceIndicator } from '@/features/spectrum/components/ConfidenceIndicator'
import { ArticleSummary } from './ArticleSummary'
import { ScoreBreakdown } from './ScoreBreakdown'
import { getLabel, getColor } from '@/features/spectrum/utils/spectrumColors'

interface AnalysisCardProps {
  analysis: ArticleAnalysis
}

function generateBriefSummary(analysis: ArticleAnalysis): string {
  const { topics, key_points } = analysis

  // Build a brief summary from topic and first key point
  let summary = `This article covers ${topics.primary_topic.toLowerCase()}`

  if (topics.secondary_topics.length > 0) {
    summary += `, touching on ${topics.secondary_topics.slice(0, 2).join(' and ').toLowerCase()}`
  }

  summary += '.'

  // Add the first key point if available
  if (key_points.length > 0) {
    summary += ` Key takeaway: ${key_points[0].statement}`
  }

  return summary
}

export function AnalysisCard({ analysis }: AnalysisCardProps) {
  const { political_leaning, article_title, source_name, article_url } = analysis
  const label = getLabel(political_leaning.score)
  const color = getColor(political_leaning.score)

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-slate-100 dark:border-slate-700">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <h2 className="text-xl font-semibold text-slate-900 dark:text-white">
              {article_title}
            </h2>
            <a
              href={article_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
            >
              {source_name}
            </a>
            {/* Brief article summary */}
            <p className="mt-3 text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
              {generateBriefSummary(analysis)}
            </p>
          </div>
          {analysis.cached && (
            <span className="flex-shrink-0 text-xs text-slate-400 bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">
              Cached
            </span>
          )}
        </div>
      </div>

      {/* Spectrum Visualization */}
      <div className="p-6 bg-slate-50 dark:bg-slate-900/50">
        <div className="mb-4">
          <SpectrumScale
            score={political_leaning.score}
            confidence={political_leaning.confidence}
            showLabels={true}
            showAllLabels={false}
            height="lg"
          />
        </div>

        {/* Score Display */}
        <div className="flex items-center justify-between mt-6">
          <div className="flex items-center gap-3">
            <div
              className="w-4 h-4 rounded-full"
              style={{ backgroundColor: color }}
            />
            <div>
              <span className="text-lg font-semibold text-slate-900 dark:text-white">
                {label}
              </span>
              <span className="ml-2 text-slate-500">
                ({political_leaning.score > 0 ? '+' : ''}{political_leaning.score.toFixed(2)})
              </span>
            </div>
          </div>
          <ConfidenceIndicator confidence={political_leaning.confidence} />
        </div>

        {/* Reasoning */}
        <div className="mt-4 p-4 bg-white dark:bg-slate-800 rounded-lg">
          <h4 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">
            Analysis Reasoning
          </h4>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            {political_leaning.reasoning}
          </p>
        </div>

        {/* Score Breakdown */}
        <ScoreBreakdown politicalLeaning={political_leaning} />
      </div>

      {/* Article Details */}
      <div className="p-6">
        <ArticleSummary analysis={analysis} />
      </div>

      {/* Footer */}
      <div className="px-6 py-3 bg-slate-50 dark:bg-slate-900/50 border-t border-slate-100 dark:border-slate-700">
        <p className="text-xs text-slate-400">
          Analyzed by {analysis.ai_provider} at {new Date(analysis.analyzed_at).toLocaleString()}
        </p>
      </div>
    </div>
  )
}
