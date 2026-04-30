'use client'

import { Users, Package, ShoppingCart, TrendingUp, Clock, CheckCircle } from 'lucide-react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { useAdminDashboard, useAdminTrend } from '@/hooks/use-admin-stats'

interface StatCardProps {
  label: string
  value: string | number
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  icon: any
  color: string
}

function StatCard({ label, value, icon: Icon, color }: StatCardProps) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  )
}

export default function AdminDashboard() {
  const dashboardQuery = useAdminDashboard()
  const trendQuery = useAdminTrend(30)

  const stats = dashboardQuery.data
  const trendData = trendQuery.data ?? []

  if (dashboardQuery.isLoading) {
    return (
      <div className="p-8 text-sm text-gray-500">正在加载仪表盘数据...</div>
    )
  }

  if (!stats) {
    return (
      <div className="p-8 text-sm text-red-500">仪表盘数据加载失败</div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">数据大盘</h1>
        <p className="text-gray-500 mt-1">龙虾超市运营概览</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard label="注册用户" value={stats.totalUsers} icon={Users} color="bg-blue-500" />
        <StatCard label="上架插件" value={stats.totalPlugins} icon={Package} color="bg-orange-500" />
        <StatCard label="总订单数" value={stats.totalOrders} icon={ShoppingCart} color="bg-green-500" />
        <StatCard
          label="平台总收入"
          value={`¥${stats.totalRevenue.toFixed(2)}`}
          icon={TrendingUp}
          color="bg-purple-500"
        />
      </div>

      {/* 趋势图表 */}
      <div className="bg-white rounded-xl p-6 shadow-sm border mb-8">
        <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-purple-500" />
          近 30 天趋势
        </h2>
        {trendQuery.isLoading ? (
          <div className="h-64 flex items-center justify-center text-sm text-gray-400">
            加载趋势数据...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 12 }}
                tickFormatter={(v) => String(v).slice(5)}
              />
              <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
              <Tooltip
                labelFormatter={(v) => `日期: ${v}`}
                contentStyle={{ fontSize: 13 }}
              />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="orderCount"
                name="订单数"
                stroke="#22c55e"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="revenue"
                name="收入 (¥)"
                stroke="#a855f7"
                strokeWidth={2}
                dot={false}
              />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="newUsers"
                name="新用户"
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <Clock className="w-4 h-4 text-orange-500" />
            待处理事项
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-gray-600">待审核插件</span>
              <span className="bg-orange-100 text-orange-600 text-xs px-2 py-1 rounded-full">
                {stats.pendingReviews}
              </span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-gray-600">待审批提现</span>
              <span className="bg-red-100 text-red-600 text-xs px-2 py-1 rounded-full">
                {stats.pendingWithdrawals}
              </span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border">
          <h2 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" />
            今日概况
          </h2>
          <div className="space-y-3">
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-gray-600">今日新增用户</span>
              <span className="font-medium">{stats.todayNewUsers}</span>
            </div>
            <div className="flex justify-between items-center py-2 border-b">
              <span className="text-sm text-gray-600">今日成交订单</span>
              <span className="font-medium">{stats.todayOrders}</span>
            </div>
            <div className="flex justify-between items-center py-2">
              <span className="text-sm text-gray-600">今日流水</span>
              <span className="font-medium text-green-600">
                ¥{stats.todayRevenue.toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
