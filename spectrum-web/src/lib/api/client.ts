import axios, { AxiosError } from 'axios'
import { SpectrumError, isApiErrorResponse } from './errors'

// Re-export error types for convenience
export { SpectrumError } from './errors'
export type { ErrorCode, ApiErrorDetail } from './errors'

// API base URL configuration
// - Development: Uses Vite proxy (/api/v1 -> localhost:8000/api/v1)
// - Production: Uses VITE_API_URL environment variable
const API_BASE_URL = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor to convert errors to SpectrumError
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    // Network errors (no response)
    if (!error.response) {
      throw SpectrumError.networkError(error.message || 'Network connection failed')
    }

    // Check if backend returned structured error
    const data = error.response.data
    if (isApiErrorResponse(data)) {
      throw SpectrumError.fromApiResponse(data)
    }

    // Legacy string error from backend
    if (typeof data === 'object' && data !== null && 'detail' in data) {
      throw SpectrumError.unknownError(String((data as { detail: unknown }).detail))
    }

    // Fallback for unexpected error formats
    throw SpectrumError.unknownError(error.message || 'An unexpected error occurred')
  }
)

// Types matching backend schemas
export interface CriterionScore {
  score: number // -1 to 1
  explanation: string
}

export interface CriteriaBreakdown {
  language_and_framing: CriterionScore
  source_selection: CriterionScore
  topic_emphasis: CriterionScore
  tone_objectivity: CriterionScore
  source_reputation: CriterionScore
}

export interface PoliticalLeaning {
  score: number // -1 to 1
  confidence: number // 0 to 1
  reasoning: string
  economic_score: number | null
  social_score: number | null
  criteria_scores?: CriteriaBreakdown
}

export interface TopicAnalysis {
  primary_topic: string
  secondary_topics: string[]
  keywords: string[]
  entities: string[]
  story_identifier: string | null
}

export interface ArticlePoint {
  id: string
  statement: string
  supporting_quote: string | null
  sentiment: 'positive' | 'negative' | 'neutral'
}

export interface ArticleAnalysis {
  article_id: string
  article_url: string
  article_title: string
  source_name: string
  political_leaning: PoliticalLeaning
  topics: TopicAnalysis
  key_points: ArticlePoint[]
  analyzed_at: string
  ai_provider: string
  cached: boolean
}

export interface AnalysisResponse {
  success: boolean
  data: ArticleAnalysis | null
  error: string | null
  cached: boolean
  processing_time_ms: number
}

export interface RelatedArticlePreview {
  url: string
  title: string
  source: string
  published_at: string | null
  snippet: string | null
}

export interface RelatedArticlesResponse {
  success: boolean
  original_keywords: string[]
  articles: RelatedArticlePreview[]
  total_found: number
  error: string | null
}

export interface BlockedSource {
  domain: string
  reason: string
}

export interface SourceCompatibility {
  supported: string[]
  partial: string[]
  blocked: BlockedSource[]
}

// Comparison types
export interface PointComparison {
  point_a: ArticlePoint
  point_b: ArticlePoint
  article_a_id: string
  article_b_id: string
  relationship: 'agrees' | 'disagrees' | 'related' | 'unrelated'
  explanation: string
}

export interface ArticleComparisonPair {
  article_a_id: string
  article_b_id: string
  same_story: boolean
  same_story_confidence: number
  leaning_difference: number
  leaning_summary: string
  shared_topics: string[]
  unique_topics_a: string[]
  unique_topics_b: string[]
  agreements: PointComparison[]
  disagreements: PointComparison[]
}

export interface MultiArticleComparison {
  articles: ArticleAnalysis[]
  pairwise_comparisons: ArticleComparisonPair[]
  leaning_spectrum: Record<string, number>
  consensus_points: string[]
  contested_points: string[]
  overall_summary: string
}

// API functions
export async function analyzeArticle(url: string): Promise<AnalysisResponse> {
  const response = await apiClient.post<AnalysisResponse>('/articles/analyze', {
    url,
    include_points: true,
    force_refresh: false,
  })
  return response.data
}

export async function findRelatedArticles(url: string): Promise<RelatedArticlesResponse> {
  const response = await apiClient.post<RelatedArticlesResponse>('/articles/related', {
    url,
    limit: 5,
  })
  return response.data
}

export async function getSourceCompatibility(): Promise<SourceCompatibility> {
  const response = await apiClient.get<SourceCompatibility>('/articles/sources')
  return response.data
}

export async function compareArticles(
  urls: string[],
  depth: 'quick' | 'full' | 'deep' = 'full'
): Promise<MultiArticleComparison> {
  const response = await apiClient.post<MultiArticleComparison>('/comparisons', {
    article_urls: urls,
    comparison_depth: depth,
  })
  return response.data
}

// Documentation types and functions
export interface DocumentationResponse {
  name: string
  filename: string
  content: string
}

export type DocName = 'readme' | 'prd' | 'architecture' | 'diagrams' | 'tech-decisions'

export async function getDocumentation(docName: DocName): Promise<DocumentationResponse> {
  const response = await apiClient.get<DocumentationResponse>(`/docs/${docName}`)
  return response.data
}
