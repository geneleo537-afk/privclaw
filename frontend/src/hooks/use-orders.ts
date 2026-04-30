import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import {
  mapOrder,
  mapOrderStatus,
  mapPageData,
  mapPaymentSession,
  unwrapResponse,
} from '@/lib/mappers'
import type { ApiResponse, PageData } from '@/types/api'

export function useOrders(params = {}) {
  return useQuery({
    queryKey: ['orders', params],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<PageData<Record<string, unknown>>>>(
        '/users/me/orders',
        { params },
      )
      return mapPageData(unwrapResponse(res.data), mapOrder)
    },
  })
}

export function useOrder(orderId: string) {
  return useQuery({
    queryKey: ['order', orderId],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>(
        `/orders/${orderId}`,
      )
      return mapOrder(unwrapResponse(res.data))
    },
    enabled: !!orderId,
  })
}

export function useCreateOrder() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (pluginId: string) => {
      const res = await apiClient.post<ApiResponse<Record<string, unknown>>>(
        '/orders',
        { plugin_id: pluginId },
      )
      return mapOrder(unwrapResponse(res.data))
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['orders'] }),
  })
}

export function useOrderStatus(orderId: string, enabled = true) {
  return useQuery({
    queryKey: ['order-status', orderId],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>(
        `/orders/${orderId}/status`,
      )
      return mapOrderStatus(unwrapResponse(res.data))
    },
    enabled: !!orderId && enabled,
    refetchInterval: enabled ? 3000 : false,
  })
}

export function usePayWithBalance() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (orderId: string) => {
      const res = await apiClient.post<ApiResponse<Record<string, unknown>>>(
        `/orders/${orderId}/pay/balance`,
      )
      return mapOrder(unwrapResponse(res.data))
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['orders'] })
      qc.invalidateQueries({ queryKey: ['wallet'] })
      qc.invalidateQueries({ queryKey: ['wallet-transactions'] })
      qc.invalidateQueries({ queryKey: ['purchases'] })
    },
  })
}

export function usePayWithAlipay() {
  return useMutation({
    mutationFn: async (orderId: string) => {
      const res = await apiClient.post<ApiResponse<Record<string, unknown>>>(
        `/orders/${orderId}/pay/alipay`,
      )
      return mapPaymentSession(unwrapResponse(res.data))
    },
  })
}

export function useDevCompletePayment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (orderId: string) => {
      const res = await apiClient.post<ApiResponse<Record<string, unknown>>>(
        `/orders/${orderId}/pay/dev-complete`,
      )
      return unwrapResponse(res.data)
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['orders'] })
      qc.invalidateQueries({ queryKey: ['purchases'] })
      qc.invalidateQueries({ queryKey: ['order-status'] })
    },
  })
}
