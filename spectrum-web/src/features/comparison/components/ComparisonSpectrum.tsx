import type { ArticleAnalysis } from '@/lib/api/client'
import { SpectrumScale } from '@/features/spectrum/components/SpectrumScale'
import { getColor, scoreToPercent } from '@/features/spectrum/utils/spectrumColors'

interface ComparisonSpectrumProps {
  articles: ArticleAnalysis[]
}

export function ComparisonSpectrum({ articles }: ComparisonSpectrumProps) {
  return (
    <div className="relative">
      {/* Scale */}
      <SpectrumScale height="lg" showLabels={true} />

      {/* Article markers */}
      <div className="absolute inset-x-0 top-0 h-4 flex items-center">
        {articles.map((article) => {
          const percent = scoreToPercent(article.political_leaning.score)
          const color = getColor(article.political_leaning.score)

          return (
            <div
              key={article.article_id}
              className="absolute transform -translate-x-1/2 group"
              style={{ left: percent + '%' }}
            >
              {/* Marker */}
              <div
                className="w-4 h-4 rounded-full border-2 border-white shadow-md cursor-pointer"
                style={{ backgroundColor: color }}
              />

              {/* Tooltip */}
              <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 hidden group-hover:block z-10">
                <div className="bg-gray-900 text-white text-xs rounded py-1 px-2 whitespace-nowrap">
                  {article.source_name}
                  <br />
                  <span className="text-gray-400">
                    Score: {article.political_leaning.score.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
