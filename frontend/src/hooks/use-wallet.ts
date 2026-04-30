import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import {
  mapPageData,
  mapPurchaseItem,
  mapWalletOverview,
  mapWalletTransaction,
  mapWithdrawalItem,
  unwrapResponse,
} from '@/lib/mappers'
import type { ApiResponse, PageData } from '@/types/api'

export function useWallet() {
  return useQuery({
    queryKey: ['wallet'],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>('/wallet')
      return mapWalletOverview(unwrapResponse(res.data))
    },
  })
}

export function useWalletTransactions(params = {}) {
  return useQuery({
    queryKey: ['wallet-transactions', params],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<PageData<Record<string, unknown>>>>(
        '/wallet/transactions',
        { params },
      )
      return mapPageData(unwrapResponse(res.data), mapWalletTransaction)
    },
  })
}

export function useWithdraw() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: {
      amount: number
      alipay_account: string
      alipay_name: string
    }) => {
      const res = await apiClient.post('/wallet/withdraw', data)
      return res.data
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['wallet'] })
      qc.invalidateQueries({ queryKey: ['wallet-transactions'] })
      qc.invalidateQueries({ queryKey: ['withdrawals'] })
    },
  })
}

export function usePurchases(params = {}) {
  return useQuery({
    queryKey: ['purchases', params],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<PageData<Record<string, unknown>>>>(
        '/users/me/purchases',
        { params },
      )
      return mapPageData(unwrapResponse(res.data), mapPurchaseItem)
    },
  })
}

export function useWithdrawals(params = {}) {
  return useQuery({
    queryKey: ['withdrawals', params],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<PageData<Record<string, unknown>>>>(
        '/wallet/withdrawals',
        { params },
      )
      return mapPageData(unwrapResponse(res.data), mapWithdrawalItem)
    },
  })
}
