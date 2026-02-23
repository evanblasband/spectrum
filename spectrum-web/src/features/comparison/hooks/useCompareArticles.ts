import { useMutation } from '@tanstack/react-query'
import { compareArticles, MultiArticleComparison } from '@/lib/api/client'
import { SpectrumError } from '@/lib/api/errors'

interface CompareArticlesParams {
  urls: string[]
  depth?: 'quick' | 'full' | 'deep'
}

export function useCompareArticles() {
  return useMutation<MultiArticleComparison, SpectrumError, CompareArticlesParams>({
    mutationFn: ({ urls, depth = 'full' }) => compareArticles(urls, depth),
  })
}
