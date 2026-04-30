'use client'

import Link from 'next/link'
import { useMemo, useState } from 'react'
import { ExternalLink, ReceiptText } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useOrders } from '@/hooks/use-orders'
import { formatDateTime } from '@/lib/utils'

const STATUS_MAP: Record<
  string,
  { label: string; variant: 'success' | 'warning' | 'destructive' | 'secondary' | 'outline' }
> = {
  paid: { label: '已完成', variant: 'success' },
  pending: { label: '待支付', variant: 'warning' },
  closed: { label: '已超时关闭', variant: 'secondary' },
  cancelled: { label: '已取消', variant: 'destructive' },
  refunded: { label: '已退款', variant: 'outline' },
}

const PAY_CHANNEL_MAP: Record<string, string> = {
  alipay: '支付宝',
  wechat: '微信支付',
  balance: '余额支付',
}

const STATUS_FILTER_OPTIONS = [
  { label: '全部', value: '' },
  { label: '已完成', value: 'paid' },
  { label: '待支付', value: 'pending' },
  { label: '已取消', value: 'cancelled' },
]

export default function OrdersPage() {
  const [statusFilter, setStatusFilter] = useState('')
  const ordersQuery = useOrders({ page_size: 50 })

  const filteredOrders = useMemo(() => {
    const items = ordersQuery.data?.items ?? []
    return items.filter((order) => !statusFilter || order.status === statusFilter)
  }, [ordersQuery.data?.items, statusFilter])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">我的订单</h1>
        <p className="text-[hsl(var(--muted-foreground))] text-sm mt-1">
          查看所有购买记录
        </p>
      </div>

      <div className="flex gap-2 flex-wrap">
        {STATUS_FILTER_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            onClick={() => setStatusFilter(opt.value)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              statusFilter === opt.value
                ? 'bg-[hsl(var(--primary))] text-white'
                : 'bg-[hsl(var(--muted)/0.5)] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {ordersQuery.isLoading ? (
        <Card>
          <CardContent className="p-12 text-center text-[hsl(var(--muted-foreground))]">
            正在加载订单...
          </CardContent>
        </Card>
      ) : ordersQuery.isError ? (
        <Card>
          <CardContent className="p-12 text-center text-red-600">
            订单加载失败，请检查登录状态或后端服务
          </CardContent>
        </Card>
      ) : filteredOrders.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <ReceiptText className="h-12 w-12 mx-auto text-[hsl(var(--muted-foreground)/0.4)] mb-3" />
            <p className="text-[hsl(var(--muted-foreground))]">暂无订单记录</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <div className="hidden md:block overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[hsl(var(--border))] text-xs text-[hsl(var(--muted-foreground))] uppercase tracking-wide">
                  <th className="px-5 py-3 text-left font-medium">订单号</th>
                  <th className="px-5 py-3 text-left font-medium">插件</th>
                  <th className="px-5 py-3 text-left font-medium">金额</th>
                  <th className="px-5 py-3 text-left font-medium">支付方式</th>
                  <th className="px-5 py-3 text-left font-medium">状态</th>
                  <th className="px-5 py-3 text-left font-medium">时间</th>
                  <th className="px-5 py-3 text-left font-medium">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[hsl(var(--border))]">
                {filteredOrders.map((order) => {
                  const status = STATUS_MAP[order.status]
                  return (
                    <tr key={order.id} className="hover:bg-[hsl(var(--muted)/0.3)] transition-colors">
                      <td className="px-5 py-4">
                        <span className="font-mono text-xs text-[hsl(var(--muted-foreground))]">
                          {order.orderNo}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm font-medium">
                          {order.pluginSnapshot.name}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm font-semibold">
                          {order.paidAmount === 0 ? '免费' : `¥${order.paidAmount.toFixed(2)}`}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-sm text-[hsl(var(--muted-foreground))]">
                          {order.payChannel ? PAY_CHANNEL_MAP[order.payChannel] : '—'}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        <Badge variant={status.variant}>{status.label}</Badge>
                      </td>
                      <td className="px-5 py-4">
                        <span className="text-xs text-[hsl(var(--muted-foreground))]">
                          {formatDateTime(order.createdAt)}
                        </span>
                      </td>
                      <td className="px-5 py-4">
                        {order.status === 'pending' ? (
                          <Button size="sm" variant="outline" asChild>
                            <Link href={`/checkout/${order.id}`}>
                              <ExternalLink className="h-3.5 w-3.5" />
                              去支付
                            </Link>
                          </Button>
                        ) : (
                          <span className="text-xs text-[hsl(var(--muted-foreground))]">—</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>

          <div className="md:hidden divide-y divide-[hsl(var(--border))]">
            {filteredOrders.map((order) => {
              const status = STATUS_MAP[order.status]
              return (
                <div key={order.id} className="p-4 space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="font-medium text-sm">{order.pluginSnapshot.name}</p>
                      <p className="font-mono text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                        {order.orderNo}
                      </p>
                    </div>
                    <Badge variant={status.variant}>{status.label}</Badge>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-semibold">
                      {order.paidAmount === 0 ? '免费' : `¥${order.paidAmount.toFixed(2)}`}
                    </span>
                    <span className="text-xs text-[hsl(var(--muted-foreground))]">
                      {formatDateTime(order.createdAt)}
                    </span>
                  </div>
                  {order.status === 'pending' && (
                    <Button size="sm" className="w-full" asChild>
                      <Link href={`/checkout/${order.id}`}>去支付</Link>
                    </Button>
                  )}
                </div>
              )
            })}
          </div>
        </Card>
      )}
    </div>
  )
}
