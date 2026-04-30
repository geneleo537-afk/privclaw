'use client'
import { useState } from 'react'
import { DataTable } from '@/components/common/data-table'
import { StatusBadge } from '@/components/common/status-badge'
import { Pagination } from '@/components/common/pagination'
import { Button } from '@/components/ui/button'
import { formatPrice } from '@/lib/utils'

interface AdminOrder {
  id: string
  order_no: string
  buyer: string
  plugin_name: string
  amount: number
  pay_channel: string
  status: string
  paid_at: string
}

const PAY_CHANNEL_MAP: Record<string, string> = {
  alipay: '支付宝',
  wechat: '微信支付',
  balance: '余额支付',
}

const mockOrders: AdminOrder[] = [
  {
    id: '1',
    order_no: 'ORD20260301001',
    buyer: '用户A',
    plugin_name: '智能代码审查助手',
    amount: 99,
    pay_channel: 'alipay',
    status: 'paid',
    paid_at: '2026-03-01 10:23',
  },
  {
    id: '2',
    order_no: 'ORD20260302002',
    buyer: '用户B',
    plugin_name: 'AI 写作助手 Pro',
    amount: 49,
    pay_channel: 'wechat',
    status: 'paid',
    paid_at: '2026-03-02 14:05',
  },
  {
    id: '3',
    order_no: 'ORD20260303003',
    buyer: '用户C',
    plugin_name: 'Git工作流自动化',
    amount: 0,
    pay_channel: 'balance',
    status: 'refunded',
    paid_at: '2026-03-03 09:11',
  },
  {
    id: '4',
    order_no: 'ORD20260304004',
    buyer: '用户D',
    plugin_name: '文档自动生成器',
    amount: 199,
    pay_channel: 'alipay',
    status: 'pending',
    paid_at: '—',
  },
  {
    id: '5',
    order_no: 'ORD20260305005',
    buyer: '用户E',
    plugin_name: '智能代码审查助手',
    amount: 99,
    pay_channel: 'alipay',
    status: 'closed',
    paid_at: '—',
  },
]

type OrderRow = Record<string, unknown> & AdminOrder

export default function AdminOrdersPage() {
  const [page, setPage] = useState(1)

  const columns = [
    { key: 'order_no', header: '订单号', className: 'font-mono text-xs' },
    { key: 'buyer', header: '买家' },
    { key: 'plugin_name', header: '插件名称' },
    {
      key: 'amount',
      header: '金额',
      render: (row: OrderRow) => formatPrice(row.amount as number),
    },
    {
      key: 'pay_channel',
      header: '支付方式',
      render: (row: OrderRow) =>
        PAY_CHANNEL_MAP[row.pay_channel as string] ?? (row.pay_channel as string),
    },
    {
      key: 'status',
      header: '状态',
      render: (row: OrderRow) => <StatusBadge status={row.status as string} />,
    },
    { key: 'paid_at', header: '支付时间' },
    {
      key: 'actions',
      header: '操作',
      render: (row: OrderRow) =>
        row.status === 'paid' ? (
          <Button
            size="sm"
            variant="outline"
            className="text-red-600 border-red-200 hover:bg-red-50"
          >
            退款
          </Button>
        ) : (
          <span className="text-xs text-gray-400">—</span>
        ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">订单管理</h1>
          <p className="text-sm text-gray-500 mt-1">查看所有订单，处理退款申请</p>
        </div>
      </div>

      {/* 桌面端表格 */}
      <div className="hidden md:block bg-white rounded-xl shadow-sm border overflow-hidden">
        <DataTable
          columns={columns as Parameters<typeof DataTable>[0]['columns']}
          data={mockOrders as OrderRow[]}
        />
        <div className="p-4">
          <Pagination page={page} total={mockOrders.length} pageSize={10} onPageChange={setPage} />
        </div>
      </div>

      {/* 移动端卡片 */}
      <div className="md:hidden space-y-3">
        {mockOrders.map((order) => (
          <div key={order.id} className="bg-white rounded-xl shadow-sm border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs text-gray-500">{order.order_no}</span>
              <StatusBadge status={order.status} />
            </div>
            <p className="font-medium text-sm">{order.plugin_name}</p>
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>买家：{order.buyer}</span>
              <span className="font-semibold">{formatPrice(order.amount)}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span>{PAY_CHANNEL_MAP[order.pay_channel] ?? order.pay_channel}</span>
              <span>{order.paid_at}</span>
            </div>
            {order.status === 'paid' && (
              <Button
                size="sm"
                variant="outline"
                className="w-full text-red-600 border-red-200 hover:bg-red-50"
              >
                退款
              </Button>
            )}
          </div>
        ))}
        <div className="py-2">
          <Pagination page={page} total={mockOrders.length} pageSize={10} onPageChange={setPage} />
        </div>
      </div>
    </div>
  )
}
