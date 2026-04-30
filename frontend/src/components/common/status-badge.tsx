import { cn } from '@/lib/utils'

const STATUS_MAP: Record<string, { label: string; className: string }> = {
  // 订单状态
  pending: { label: '待支付', className: 'bg-yellow-100 text-yellow-700' },
  paid: { label: '已支付', className: 'bg-green-100 text-green-700' },
  closed: { label: '已关闭', className: 'bg-gray-100 text-gray-600' },
  cancelled: { label: '已取消', className: 'bg-gray-100 text-gray-600' },
  refunded: { label: '已退款', className: 'bg-red-100 text-red-600' },
  // 插件状态
  draft: { label: '草稿', className: 'bg-gray-100 text-gray-600' },
  published: { label: '已发布', className: 'bg-green-100 text-green-700' },
  suspended: { label: '已下架', className: 'bg-red-100 text-red-600' },
  // 用户状态
  active: { label: '正常', className: 'bg-green-100 text-green-700' },
  banned: { label: '已封禁', className: 'bg-red-100 text-red-600' },
  // 提现状态
  approved: { label: '已批准', className: 'bg-blue-100 text-blue-700' },
  rejected: { label: '已驳回', className: 'bg-red-100 text-red-600' },
  completed: { label: '已完成', className: 'bg-green-100 text-green-700' },
}

export function StatusBadge({ status }: { status: string }) {
  const conf = STATUS_MAP[status] ?? { label: status, className: 'bg-gray-100 text-gray-600' }
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium',
        conf.className,
      )}
    >
      {conf.label}
    </span>
  )
}
