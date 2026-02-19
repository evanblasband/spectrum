import { useMutation } from '@tanstack/react-query'
import { analyzeArticle, AnalysisResponse } from '@/lib/api/client'
import { SpectrumError } from '@/lib/api/errors'

export function useAnalyzeArticle() {
  return useMutation<AnalysisResponse, SpectrumError, string>({
    mutationFn: analyzeArticle,
  })
}
