import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import {
  mapPageData,
  mapPlugin,
  mapPluginListItem,
  mapPluginVersion,
  unwrapResponse,
} from '@/lib/mappers'
import type { ApiResponse, PageData } from '@/types/api'

interface PluginListParams {
  page?: number
  page_size?: number
  search?: string
  category_id?: string
  category?: string
  sort_by?: string
}

export function usePlugins(params: PluginListParams = {}) {
  return useQuery({
    queryKey: ['plugins', params],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<PageData<Record<string, unknown>>>>(
        '/plugins',
        { params },
      )
      return mapPageData(unwrapResponse(res.data), mapPluginListItem)
    },
    staleTime: 30_000,
  })
}

export function usePlugin(identifier: string) {
  return useQuery({
    queryKey: ['plugin', identifier],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>(
        `/plugins/${encodeURIComponent(identifier)}`,
      )
      return mapPlugin(unwrapResponse(res.data))
    },
    enabled: !!identifier,
  })
}

export function usePluginVersions(pluginId?: string) {
  return useQuery({
    queryKey: ['plugin-versions', pluginId],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>[]>>(
        `/plugins/${pluginId}/versions`,
      )
      return unwrapResponse(res.data).map(mapPluginVersion)
    },
    enabled: !!pluginId,
  })
}

export function useMyPlugins(params = {}) {
  return useQuery({
    queryKey: ['my-plugins', params],
    queryFn: async () => {
      const res = await apiClient.get('/users/me/plugins', { params })
      return res.data
    },
  })
}
