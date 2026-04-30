import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import {
  mapPageData,
  mapReview,
  mapReviewSummary,
  unwrapResponse,
} from '@/lib/mappers'
import type { ApiResponse, PageData } from '@/types/api'
import type { CreateReviewPayload } from '@/types/review'

interface ReviewListParams {
  page?: number
  page_size?: number
}

export function useReviews(pluginId: string | undefined, params: ReviewListParams = {}) {
  return useQuery({
    queryKey: ['reviews', pluginId, params],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<PageData<Record<string, unknown>>>>(
        `/plugins/${pluginId}/reviews`,
        { params },
      )
      return mapPageData(unwrapResponse(res.data), mapReview)
    },
    enabled: !!pluginId,
    staleTime: 30_000,
  })
}

export function useReviewSummary(pluginId: string | undefined) {
  return useQuery({
    queryKey: ['review-summary', pluginId],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>(
        `/plugins/${pluginId}/reviews/summary`,
      )
      return mapReviewSummary(unwrapResponse(res.data))
    },
    enabled: !!pluginId,
    staleTime: 30_000,
  })
}

export function useCreateReview(pluginId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CreateReviewPayload) => {
      const res = await apiClient.post<ApiResponse<Record<string, unknown>>>(
        `/plugins/${pluginId}/reviews`,
        payload,
      )
      return mapReview(unwrapResponse(res.data))
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', pluginId] })
      queryClient.invalidateQueries({ queryKey: ['review-summary', pluginId] })
      queryClient.invalidateQueries({ queryKey: ['plugin'] })
    },
  })
}

export function useDeleteReview(pluginId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (reviewId: string) => {
      const res = await apiClient.delete<ApiResponse<Record<string, unknown>>>(
        `/plugins/${pluginId}/reviews/${reviewId}`,
      )
      return unwrapResponse(res.data)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews', pluginId] })
      queryClient.invalidateQueries({ queryKey: ['review-summary', pluginId] })
      queryClient.invalidateQueries({ queryKey: ['plugin'] })
    },
  })
}
