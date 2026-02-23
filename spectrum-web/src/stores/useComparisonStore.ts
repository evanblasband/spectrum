import { create } from 'zustand'
import type { ArticleAnalysis, RelatedArticlePreview } from '@/lib/api/client'

// A pending article is one from related articles that hasn't been analyzed yet
export interface PendingArticle {
  url: string
  title: string
  source: string
  isPending: true
}

export type ComparisonArticle = ArticleAnalysis | PendingArticle

export function isPendingArticle(article: ComparisonArticle): article is PendingArticle {
  return 'isPending' in article && article.isPending === true
}

export function getArticleId(article: ComparisonArticle): string {
  if (isPendingArticle(article)) {
    return article.url // Use URL as ID for pending articles
  }
  return article.article_id
}

interface ComparisonState {
  selectedArticles: ComparisonArticle[]
  addArticle: (article: ArticleAnalysis) => void
  addPendingArticle: (preview: RelatedArticlePreview) => void
  removeArticle: (id: string) => void
  clearArticles: () => void
  isSelected: (id: string) => boolean
  hasPendingArticles: () => boolean
  // Replace a pending article with its analyzed version
  replacePendingWithAnalyzed: (url: string, analysis: ArticleAnalysis) => void
}

export const useComparisonStore = create<ComparisonState>((set, get) => ({
  selectedArticles: [],

  addArticle: (article) => {
    const current = get().selectedArticles
    if (current.length >= 5) return // Max 5 articles
    if (current.some((a) => getArticleId(a) === article.article_id)) return
    set({ selectedArticles: [...current, article] })
  },

  addPendingArticle: (preview) => {
    const current = get().selectedArticles
    if (current.length >= 5) return // Max 5 articles
    if (current.some((a) => getArticleId(a) === preview.url)) return // Already added

    const pending: PendingArticle = {
      url: preview.url,
      title: preview.title,
      source: preview.source,
      isPending: true,
    }
    set({ selectedArticles: [...current, pending] })
  },

  removeArticle: (id) => {
    set({
      selectedArticles: get().selectedArticles.filter(
        (a) => getArticleId(a) !== id
      ),
    })
  },

  clearArticles: () => {
    set({ selectedArticles: [] })
  },

  isSelected: (id) => {
    return get().selectedArticles.some((a) => getArticleId(a) === id)
  },

  hasPendingArticles: () => {
    return get().selectedArticles.some(isPendingArticle)
  },

  replacePendingWithAnalyzed: (url, analysis) => {
    set({
      selectedArticles: get().selectedArticles.map((a) => {
        if (isPendingArticle(a) && a.url === url) {
          return analysis
        }
        return a
      }),
    })
  },
}))
