import { useQuery } from '@tanstack/react-query'
import { getSourceCompatibility, type SourceCompatibility } from '@/lib/api/client'

export function useSourceCompatibility() {
  return useQuery<SourceCompatibility>({
    queryKey: ['sourceCompatibility'],
    queryFn: getSourceCompatibility,
    staleTime: 1000 * 60 * 60, // Cache for 1 hour
    gcTime: 1000 * 60 * 60 * 24, // Keep in cache for 24 hours
  })
}
