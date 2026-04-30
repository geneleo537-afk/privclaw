'use client'
import { useState } from 'react'
import { DataTable } from '@/components/common/data-table'
import { StatusBadge } from '@/components/common/status-badge'
import { Pagination } from '@/components/common/pagination'
import { Button } from '@/components/ui/button'
import { formatPrice } from '@/lib/utils'

interface WithdrawalRecord {
  id: string
  applicant: string
  amount: number
  alipay_account: string
  alipay_name: string
  applied_at: string
  status: string
}

const mockWithdrawals: WithdrawalRecord[] = [
  {
    id: '1',
    applicant: '张开发',
    amount: 500,
    alipay_account: 'dev_zhang@example.com',
    alipay_name: '张三',
    applied_at: '2026-03-08 10:30',
    status: 'pending',
  },
  {
    id: '2',
    applicant: '李程序',
    amount: 1200,
    alipay_account: '13800138000',
    alipay_name: '李四',
    applied_at: '2026-03-07 15:22',
    status: 'pending',
  },
  {
    id: '3',
    applicant: '王工程',
    amount: 300,
    alipay_account: 'wanggong@example.com',
    alipay_name: '王五',
    applied_at: '2026-03-06 09:15',
    status: 'approved',
  },
  {
    id: '4',
    applicant: '赵设计',
    amount: 800,
    alipay_account: '18900189000',
    alipay_name: '赵六',
    applied_at: '2026-03-05 11:40',
    status: 'rejected',
  },
  {
    id: '5',
    applicant: '刘运营',
    amount: 2000,
    alipay_account: 'liu_ops@example.com',
    alipay_name: '刘七',
    applied_at: '2026-03-01 14:00',
    status: 'completed',
  },
]

type WithdrawalRow = Record<string, unknown> & WithdrawalRecord

export default function AdminWithdrawalsPage() {
  const [page, setPage] = useState(1)

  const columns = [
    { key: 'applicant', header: '申请人', className: 'font-medium' },
    {
      key: 'amount',
      header: '金额',
      render: (row: WithdrawalRow) => (
        <span className="font-semibold text-gray-900">
          {formatPrice(row.amount as number)}
        </span>
      ),
    },
    { key: 'alipay_account', header: '支付宝账号', className: 'font-mono text-xs' },
    { key: 'alipay_name', header: '真实姓名' },
    { key: 'applied_at', header: '申请时间' },
    {
      key: 'status',
      header: '状态',
      render: (row: WithdrawalRow) => <StatusBadge status={row.status as string} />,
    },
    {
      key: 'actions',
      header: '操作',
      render: (row: WithdrawalRow) =>
        row.status === 'pending' ? (
          <div className="flex gap-2">
            <Button
              size="sm"
              className="bg-green-500 hover:bg-green-600 text-white"
            >
              批准
            </Button>
            <Button
              size="sm"
              variant="outline"
              className="text-red-600 border-red-200 hover:bg-red-50"
            >
              驳回
            </Button>
          </div>
        ) : (
          <span className="text-xs text-gray-400">已处理</span>
        ),
    },
  ]

  const pendingCount = mockWithdrawals.filter((w) => w.status === 'pending').length

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">提现审批</h1>
          <p className="text-sm text-gray-500 mt-1">审批开发者提现申请</p>
        </div>
        <div className="bg-orange-50 border border-orange-200 rounded-lg px-4 py-2 text-sm text-orange-700">
          待审批：<span className="font-bold">{pendingCount}</span> 笔
        </div>
      </div>

      {/* 桌面端表格 */}
      <div className="hidden md:block bg-white rounded-xl shadow-sm border overflow-hidden">
        <DataTable
          columns={columns as Parameters<typeof DataTable>[0]['columns']}
          data={mockWithdrawals as WithdrawalRow[]}
        />
        <div className="p-4">
          <Pagination
            page={page}
            total={mockWithdrawals.length}
            pageSize={10}
            onPageChange={setPage}
          />
        </div>
      </div>

      {/* 移动端卡片 */}
      <div className="md:hidden space-y-3">
        {mockWithdrawals.map((w) => (
          <div key={w.id} className="bg-white rounded-xl shadow-sm border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-medium">{w.applicant}</span>
              <StatusBadge status={w.status} />
            </div>
            <p className="text-xl font-bold text-gray-900">{formatPrice(w.amount)}</p>
            <div className="text-sm text-gray-600 space-y-0.5">
              <p>支付宝：<span className="font-mono text-xs">{w.alipay_account}</span></p>
              <p>姓名：{w.alipay_name}</p>
            </div>
            <p className="text-xs text-gray-400">{w.applied_at}</p>
            {w.status === 'pending' && (
              <div className="flex gap-2">
                <Button
                  size="sm"
                  className="flex-1 bg-green-500 hover:bg-green-600 text-white"
                >
                  批准
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 text-red-600 border-red-200 hover:bg-red-50"
                >
                  驳回
                </Button>
              </div>
            )}
          </div>
        ))}
        <div className="py-2">
          <Pagination
            page={page}
            total={mockWithdrawals.length}
            pageSize={10}
            onPageChange={setPage}
          />
        </div>
      </div>
    </div>
  )
}
