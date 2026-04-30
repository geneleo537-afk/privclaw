import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import { mapDeveloperTrendDataPoint, unwrapResponse } from '@/lib/mappers'
import type { ApiResponse } from '@/types/api'

export function useDeveloperTrend(days: number = 30) {
  return useQuery({
    queryKey: ['developer-trend', days],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>(
        '/users/me/stats/trend',
        { params: { days } },
      )
      const data = unwrapResponse(res.data)
      const points = Array.isArray(data.points)
        ? data.points.map((p: Record<string, unknown>) => mapDeveloperTrendDataPoint(p))
        : []
      return points
    },
    staleTime: 60_000,
  })
}
