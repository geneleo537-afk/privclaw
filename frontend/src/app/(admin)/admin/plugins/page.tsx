'use client'
import { useState } from 'react'
import { DataTable } from '@/components/common/data-table'
import { StatusBadge } from '@/components/common/status-badge'
import { Pagination } from '@/components/common/pagination'
import { Button } from '@/components/ui/button'
import { formatPrice } from '@/lib/utils'

interface AdminPlugin {
  id: string
  name: string
  developer: string
  price: number
  status: string
  download_count: number
  created_at: string
}

const mockPlugins: AdminPlugin[] = [
  {
    id: '1',
    name: '智能代码审查助手',
    developer: '张开发',
    price: 99,
    status: 'published',
    download_count: 156,
    created_at: '2026-03-01',
  },
  {
    id: '2',
    name: 'Git工作流自动化',
    developer: '李程序',
    price: 49,
    status: 'draft',
    download_count: 0,
    created_at: '2026-03-05',
  },
  {
    id: '3',
    name: '文档自动生成器',
    developer: '王工程',
    price: 0,
    status: 'suspended',
    download_count: 89,
    created_at: '2026-02-20',
  },
]

type PluginRow = Record<string, unknown> & AdminPlugin

export default function AdminPluginsPage() {
  const [page, setPage] = useState(1)
  const [filterStatus, setFilterStatus] = useState<string>('all')

  const filteredData =
    filterStatus === 'all'
      ? mockPlugins
      : mockPlugins.filter((p) => p.status === filterStatus)

  const columns = [
    { key: 'name', header: '插件名称', className: 'font-medium' },
    { key: 'developer', header: '开发者' },
    {
      key: 'price',
      header: '价格',
      render: (row: PluginRow) => formatPrice(row.price as number),
    },
    {
      key: 'status',
      header: '状态',
      render: (row: PluginRow) => <StatusBadge status={row.status as string} />,
    },
    { key: 'download_count', header: '下载量' },
    { key: 'created_at', header: '发布时间' },
    {
      key: 'actions',
      header: '操作',
      render: (row: PluginRow) => (
        <div className="flex gap-2">
          {row.status === 'published' && (
            <Button
              size="sm"
              variant="outline"
              className="text-red-600 border-red-200 hover:bg-red-50"
            >
              下架
            </Button>
          )}
          {row.status === 'suspended' && (
            <Button
              size="sm"
              variant="outline"
              className="text-green-600 border-green-200 hover:bg-green-50"
            >
              恢复
            </Button>
          )}
          {row.status === 'draft' && (
            <Button size="sm" className="bg-orange-500 hover:bg-orange-600 text-white">
              审核通过
            </Button>
          )}
        </div>
      ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">插件管理</h1>
          <p className="text-sm text-gray-500 mt-1">审核、上下架插件</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant={filterStatus === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterStatus('all')}
          >
            全部
          </Button>
          <Button
            variant={filterStatus === 'draft' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterStatus('draft')}
          >
            待审核
          </Button>
          <Button
            variant={filterStatus === 'suspended' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setFilterStatus('suspended')}
          >
            已下架
          </Button>
        </div>
      </div>

      {/* 桌面端表格 */}
      <div className="hidden md:block bg-white rounded-xl shadow-sm border overflow-hidden">
        <DataTable columns={columns as Parameters<typeof DataTable>[0]['columns']} data={filteredData as PluginRow[]} />
        <div className="p-4">
          <Pagination page={page} total={filteredData.length} pageSize={10} onPageChange={setPage} />
        </div>
      </div>

      {/* 移动端卡片 */}
      <div className="md:hidden space-y-3">
        {filteredData.map((p) => (
          <div key={p.id} className="bg-white rounded-xl shadow-sm border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-medium text-sm">{p.name}</span>
              <StatusBadge status={p.status} />
            </div>
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>{p.developer}</span>
              <span className="font-semibold">{formatPrice(p.price)}</span>
            </div>
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span>{p.download_count} 次下载</span>
              <span>{p.created_at}</span>
            </div>
            <div className="flex gap-2">
              {p.status === 'published' && (
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 text-red-600 border-red-200 hover:bg-red-50"
                >
                  下架
                </Button>
              )}
              {p.status === 'suspended' && (
                <Button
                  size="sm"
                  variant="outline"
                  className="flex-1 text-green-600 border-green-200 hover:bg-green-50"
                >
                  恢复
                </Button>
              )}
              {p.status === 'draft' && (
                <Button size="sm" className="flex-1 bg-orange-500 hover:bg-orange-600 text-white">
                  审核通过
                </Button>
              )}
            </div>
          </div>
        ))}
        <div className="py-2">
          <Pagination page={page} total={filteredData.length} pageSize={10} onPageChange={setPage} />
        </div>
      </div>
    </div>
  )
}
