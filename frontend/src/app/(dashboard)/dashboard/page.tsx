'use client'

import Link from 'next/link'
import { ShoppingBag, Package, Code2, Wallet, ArrowRight, TrendingUp, Star } from 'lucide-react'
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useOrders } from '@/hooks/use-orders'
import { useDeveloperTrend } from '@/hooks/use-developer-stats'
import { useWallet, usePurchases } from '@/hooks/use-wallet'
import { useAuthStore } from '@/stores/auth-store'
import { formatPrice } from '@/lib/utils'

const QUICK_CARDS = [
  {
    key: 'orders',
    icon: ShoppingBag,
    title: '我的订单',
    desc: '查看所有购买记录',
    href: '/dashboard/orders',
    color: 'text-blue-500 bg-blue-50',
    devOnly: false,
  },
  {
    key: 'purchases',
    icon: Package,
    title: '已购插件',
    desc: '下载已购买的插件',
    href: '/dashboard/purchases',
    color: 'text-green-500 bg-green-50',
    devOnly: false,
  },
  {
    key: 'plugins',
    icon: Code2,
    title: '我的插件',
    desc: '管理已发布的插件',
    href: '/dashboard/plugins',
    color: 'text-purple-500 bg-purple-50',
    devOnly: true,
  },
  {
    key: 'wallet',
    icon: Wallet,
    title: '我的钱包',
    desc: '收益提现与流水',
    href: '/dashboard/wallet',
    color: 'text-[hsl(var(--primary))] bg-orange-50',
    devOnly: true,
  },
] as const

const STATUS_MAP: Record<string, { label: string; variant: 'success' | 'warning' | 'destructive' | 'secondary' }> = {
  paid: { label: '已完成', variant: 'success' },
  pending: { label: '待支付', variant: 'warning' },
  closed: { label: '已关闭', variant: 'secondary' },
  cancelled: { label: '已取消', variant: 'destructive' },
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const isDeveloper = user?.role === 'developer' || user?.role === 'admin'
  const ordersQuery = useOrders({ page_size: 3 })
  const walletQuery = useWallet()
  const purchasesTotalQuery = usePurchases({ page_size: 1 })
  const trendQuery = useDeveloperTrend(30)

  const quickCounts: Record<string, number | undefined> = {
    orders:    ordersQuery.data?.total,
    purchases: purchasesTotalQuery.data?.total,
  }
  const recentOrders = ordersQuery.data?.items?.map((order) => ({
    id: order.id,
    name: order.pluginSnapshot.name,
    amount: order.paidAmount,
    status: order.status,
    date: order.createdAt.slice(0, 10),
  })) ?? []

  const greeting = (() => {
    const hour = new Date().getHours()
    if (hour < 6) return '深夜好'
    if (hour < 12) return '早上好'
    if (hour < 18) return '下午好'
    return '晚上好'
  })()

  return (
    <div className="space-y-8">
      {/* 欢迎区 */}
      <div className="rounded-2xl lobster-gradient-soft border border-orange-100 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[hsl(var(--muted-foreground))] text-sm">{greeting}，</p>
            <h1 className="text-2xl font-bold mt-0.5">
              {user?.nickname ?? '用户'} 👋
            </h1>
            <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
              欢迎使用 🦞 控制台
            </p>
          </div>
          <span className="text-6xl hidden sm:block">🦞</span>
        </div>
      </div>

      {/* 概览统计 */}
      {isDeveloper && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: '总收入', value: formatPrice(walletQuery.data?.totalEarned ?? 0), icon: TrendingUp, color: 'text-green-600' },
            { label: '可用余额', value: formatPrice(walletQuery.data?.balance ?? 0), icon: Wallet, color: 'text-[hsl(var(--primary))]' },
            { label: '订单数', value: `${ordersQuery.data?.total ?? 0} 单`, icon: Package, color: 'text-blue-600' },
            { label: '最近状态', value: ordersQuery.data?.items?.[0]?.status ?? '暂无', icon: Star, color: 'text-amber-500' },
          ].map((stat) => {
            const Icon = stat.icon
            return (
              <Card key={stat.label}>
                <CardContent className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs text-[hsl(var(--muted-foreground))]">{stat.label}</p>
                    <Icon className={`h-4 w-4 ${stat.color}`} />
                  </div>
                  <p className={`text-xl font-bold ${stat.color}`}>{stat.value}</p>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* 开发者收入趋势 */}
      {isDeveloper && trendQuery.data && trendQuery.data.length > 0 && (
        <Card>
          <CardContent className="p-5">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="h-4 w-4 text-green-600" />
              <h2 className="text-sm font-semibold">近 30 天收入趋势</h2>
            </div>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trendQuery.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => String(v).slice(5)}
                />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  labelFormatter={(v) => `日期: ${v}`}
                  contentStyle={{ fontSize: 12 }}
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  name="收入 (¥)"
                  stroke="#22c55e"
                  fill="#dcfce7"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* 快速入口 */}
      <div>
        <h2 className="text-lg font-semibold mb-4">快速入口</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {QUICK_CARDS
            .filter((card) => !card.devOnly || isDeveloper)
            .map((card) => {
              const Icon = card.icon
              return (
                <Link key={card.href} href={card.href}>
                  <Card className="h-full hover:shadow-md hover:-translate-y-0.5 transition-all duration-200 cursor-pointer group">
                    <CardContent className="p-5">
                      <div className={`inline-flex h-10 w-10 items-center justify-center rounded-xl ${card.color} mb-3`}>
                        <Icon className="h-5 w-5" />
                      </div>
                      <div className="flex items-center justify-between mb-1">
                        <h3 className="font-semibold text-sm group-hover:text-[hsl(var(--primary))] transition-colors">
                          {card.title}
                        </h3>
                        {quickCounts[card.key] !== undefined && (
                          <Badge variant="secondary" className="text-xs">
                            {quickCounts[card.key]}
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">{card.desc}</p>
                    </CardContent>
                  </Card>
                </Link>
              )
            })}
        </div>
      </div>

      {/* 最近订单 */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">最近订单</h2>
          <Button variant="ghost" size="sm" asChild>
            <Link href="/dashboard/orders">
              查看全部
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </Button>
        </div>

        <Card>
          <CardContent className="p-0">
            {ordersQuery.isLoading ? (
              <div className="divide-y divide-[hsl(var(--border))]">
                {Array.from({ length: 3 }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between px-5 py-4">
                    <div className="space-y-1.5">
                      <div className="h-3.5 w-36 rounded bg-gray-100 animate-pulse" />
                      <div className="h-3 w-20 rounded bg-gray-100 animate-pulse" />
                    </div>
                    <div className="h-5 w-16 rounded bg-gray-100 animate-pulse" />
                  </div>
                ))}
              </div>
            ) : recentOrders.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-center">
                <ShoppingBag className="h-8 w-8 text-gray-200 mb-3" />
                <p className="text-sm text-[hsl(var(--muted-foreground))]">暂无订单记录</p>
                <Button variant="ghost" size="sm" className="mt-2" asChild>
                  <Link href="/plugins">浏览能力库</Link>
                </Button>
              </div>
            ) : (
              <div className="divide-y divide-[hsl(var(--border))]">
                {recentOrders.map((order) => {
                  const status = STATUS_MAP[order.status]
                  return (
                    <div key={order.id} className="flex items-center justify-between px-5 py-4">
                      <div>
                        <p className="text-sm font-medium">{order.name}</p>
                        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{order.date}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <Badge variant={status.variant}>{status.label}</Badge>
                        <span className="text-sm font-semibold">
                          {order.amount === 0 ? '免费' : `¥${order.amount.toFixed(2)}`}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
