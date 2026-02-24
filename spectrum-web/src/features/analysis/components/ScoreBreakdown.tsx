import { useState } from 'react'
import type { PoliticalLeaning, CriteriaBreakdown } from '@/lib/api/client'
import { MiniSpectrum } from '@/features/spectrum/components/MiniSpectrum'

interface ScoreBreakdownProps {
  politicalLeaning: PoliticalLeaning
}

const CRITERIA_LABELS: Record<keyof CriteriaBreakdown, string> = {
  language_and_framing: 'Language & Framing',
  source_selection: 'Source Selection',
  topic_emphasis: 'Topic Emphasis',
  tone_objectivity: 'Tone & Objectivity',
  source_reputation: 'Source Reputation',
}

const CRITERIA_ORDER: (keyof CriteriaBreakdown)[] = [
  'language_and_framing',
  'source_selection',
  'topic_emphasis',
  'tone_objectivity',
  'source_reputation',
]

export function ScoreBreakdown({ politicalLeaning }: ScoreBreakdownProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const { criteria_scores, economic_score, social_score } = politicalLeaning

  if (!criteria_scores) {
    return null
  }

  return (
    <div className="mt-4">
      {/* Accordion Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 bg-slate-100 dark:bg-slate-700 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
      >
        <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
          How was this score calculated?
        </span>
        <svg
          className={`w-5 h-5 text-slate-500 dark:text-slate-400 transition-transform duration-200 ${
            isExpanded ? 'rotate-90' : ''
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
        </svg>
      </button>

      {/* Accordion Content */}
      <div
        className={`overflow-hidden transition-all duration-300 ease-in-out ${
          isExpanded ? 'max-h-[1000px] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="mt-3 space-y-4 p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          {/* Criteria Scores */}
          <div className="space-y-4">
            {CRITERIA_ORDER.map((key) => {
              const criterion = criteria_scores[key]
              return (
                <div key={key} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                      {CRITERIA_LABELS[key]}
                    </span>
                    <span className="text-xs text-slate-500 dark:text-slate-400">
                      {criterion.score > 0 ? '+' : ''}
                      {criterion.score.toFixed(2)}
                    </span>
                  </div>
                  <MiniSpectrum score={criterion.score} size="md" />
                  <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                    {criterion.explanation}
                  </p>
                </div>
              )
            })}
          </div>

          {/* Economic & Social Scores */}
          {(economic_score !== null || social_score !== null) && (
            <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
              <h5 className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-3">
                Dimension Scores
              </h5>
              <div className="grid grid-cols-2 gap-4">
                {economic_score !== null && (
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-400">Economic</span>
                      <span className="text-xs text-slate-500 dark:text-slate-400">
                        {economic_score > 0 ? '+' : ''}
                        {economic_score.toFixed(2)}
                      </span>
                    </div>
                    <MiniSpectrum score={economic_score} size="sm" />
                  </div>
                )}
                {social_score !== null && (
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-slate-600 dark:text-slate-400">Social</span>
                      <span className="text-xs text-slate-500 dark:text-slate-400">
                        {social_score > 0 ? '+' : ''}
                        {social_score.toFixed(2)}
                      </span>
                    </div>
                    <MiniSpectrum score={social_score} size="sm" />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
