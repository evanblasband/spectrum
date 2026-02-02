import { useQuery } from '@tanstack/react-query'
import { findRelatedArticles, RelatedArticlesResponse } from '@/lib/api/client'

export function useFindRelated(url: string | null) {
  return useQuery<RelatedArticlesResponse, Error>({
    queryKey: ['related', url],
    queryFn: () => findRelatedArticles(url!),
    enabled: !!url,
  })
}
