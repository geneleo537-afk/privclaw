import { useQuery } from '@tanstack/react-query'
import apiClient from '@/lib/api-client'
import { mapTrendDataPoint, unwrapResponse } from '@/lib/mappers'
import type { ApiResponse } from '@/types/api'

interface DashboardData {
  totalUsers: number
  totalPlugins: number
  totalOrders: number
  totalRevenue: number
  pendingWithdrawals: number
  todayOrders: number
  todayRevenue: number
  todayNewUsers: number
  pendingReviews: number
}

function mapDashboard(raw: Record<string, unknown>): DashboardData {
  const toNum = (v: unknown) => {
    if (typeof v === 'number') return v
    if (typeof v === 'string') return Number(v) || 0
    return 0
  }
  return {
    totalUsers: toNum(raw.total_users),
    totalPlugins: toNum(raw.total_plugins),
    totalOrders: toNum(raw.total_orders),
    totalRevenue: toNum(raw.total_revenue),
    pendingWithdrawals: toNum(raw.pending_withdrawals),
    todayOrders: toNum(raw.today_orders),
    todayRevenue: toNum(raw.today_revenue),
    todayNewUsers: toNum(raw.today_new_users),
    pendingReviews: toNum(raw.pending_reviews),
  }
}

export function useAdminDashboard() {
  return useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>(
        '/admin/dashboard',
      )
      return mapDashboard(unwrapResponse(res.data))
    },
  })
}

export function useAdminTrend(days: number = 30) {
  return useQuery({
    queryKey: ['admin-trend', days],
    queryFn: async () => {
      const res = await apiClient.get<ApiResponse<Record<string, unknown>>>(
        '/admin/stats/trend',
        { params: { days } },
      )
      const data = unwrapResponse(res.data)
      const points = Array.isArray(data.points)
        ? data.points.map((p: Record<string, unknown>) => mapTrendDataPoint(p))
        : []
      return points
    },
    staleTime: 60_000,
  })
}
