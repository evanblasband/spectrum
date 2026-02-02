import { create } from 'zustand'
import type { ArticleAnalysis } from '@/lib/api/client'

interface ComparisonState {
  selectedArticles: ArticleAnalysis[]
  addArticle: (article: ArticleAnalysis) => void
  removeArticle: (articleId: string) => void
  clearArticles: () => void
  isSelected: (articleId: string) => boolean
}

export const useComparisonStore = create<ComparisonState>((set, get) => ({
  selectedArticles: [],

  addArticle: (article) => {
    const current = get().selectedArticles
    if (current.length >= 5) return // Max 5 articles
    if (current.some((a) => a.article_id === article.article_id)) return // Already selected
    set({ selectedArticles: [...current, article] })
  },

  removeArticle: (articleId) => {
    set({
      selectedArticles: get().selectedArticles.filter(
        (a) => a.article_id !== articleId
      ),
    })
  },

  clearArticles: () => {
    set({ selectedArticles: [] })
  },

  isSelected: (articleId) => {
    return get().selectedArticles.some((a) => a.article_id === articleId)
  },
}))
