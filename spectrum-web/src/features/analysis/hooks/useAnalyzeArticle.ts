import { useMutation } from '@tanstack/react-query'
import { analyzeArticle, AnalysisResponse } from '@/lib/api/client'

export function useAnalyzeArticle() {
  return useMutation<AnalysisResponse, Error, string>({
    mutationFn: analyzeArticle,
  })
}
