'use client'

import Link from 'next/link'
import { Plus, Eye, Edit, BarChart3, TrendingUp } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatPrice, formatNumber, formatDateTime } from '@/lib/utils'
import type { PluginStatus } from '@/types/plugin'

interface MyPlugin {
  id: string
  name: string
  slug: string
  status: PluginStatus
  price: number
  downloadCount: number
  avgRating: number
  revenue: number
  createdAt: string
  currentVersion: string
}

const MOCK_MY_PLUGINS: MyPlugin[] = [
  {
    id: '1',
    name: 'AI 写作助手 Pro',
    slug: 'ai-writer-pro',
    status: 'published',
    price: 49,
    downloadCount: 12480,
    avgRating: 4.8,
    revenue: 611520,
    createdAt: '2024-03-15T08:00:00Z',
    currentVersion: '2.3.1',
  },
  {
    id: '2',
    name: '代码质量卫士',
    slug: 'code-guardian',
    status: 'published',
    price: 39,
    downloadCount: 8920,
    avgRating: 4.7,
    revenue: 347880,
    createdAt: '2024-06-01T08:00:00Z',
    currentVersion: '1.5.0',
  },
  {
    id: '3',
    name: '企业数据报表引擎',
    slug: 'enterprise-report',
    status: 'draft',
    price: 99,
    downloadCount: 0,
    avgRating: 0,
    revenue: 0,
    createdAt: '2024-12-01T08:00:00Z',
    currentVersion: '0.1.0',
  },
]

const STATUS_CONFIG: Record<PluginStatus, { label: string; variant: 'success' | 'secondary' | 'warning' }> = {
  published: { label: '已发布', variant: 'success' },
  draft: { label: '草稿', variant: 'secondary' },
  suspended: { label: '已暂停', variant: 'warning' },
}

export default function MyPluginsPage() {
  const totalRevenue = MOCK_MY_PLUGINS.reduce((sum, p) => sum + p.revenue, 0)
  const totalDownloads = MOCK_MY_PLUGINS.reduce((sum, p) => sum + p.downloadCount, 0)

  return (
    <div className="space-y-6">
      {/* 页头 */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">我的插件</h1>
          <p className="text-[hsl(var(--muted-foreground))] text-sm mt-1">
            管理和监控你发布的所有插件
          </p>
        </div>
        <Button asChild>
          <Link href="/dashboard/plugins/new">
            <Plus className="h-4 w-4" />
            发布新插件
          </Link>
        </Button>
      </div>

      {/* 汇总统计 */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: '累计收入', value: formatPrice(totalRevenue / 100), icon: TrendingUp, color: 'text-green-600' },
          { label: '总下载量', value: `${formatNumber(totalDownloads)} 次`, icon: BarChart3, color: 'text-blue-600' },
          { label: '已上架插件', value: `${MOCK_MY_PLUGINS.filter((p) => p.status === 'published').length} 个`, icon: Eye, color: 'text-[hsl(var(--primary))]' },
        ].map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.label}>
              <CardContent className="p-4 flex items-center gap-3">
                <div className={`h-10 w-10 rounded-lg bg-current/10 flex items-center justify-center ${stat.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">{stat.label}</p>
                  <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* 插件列表 */}
      <div className="space-y-3">
        {MOCK_MY_PLUGINS.map((plugin) => {
          const statusCfg = STATUS_CONFIG[plugin.status]
          return (
            <Card key={plugin.id} className="hover:shadow-sm transition-shadow">
              <CardContent className="p-5">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  {/* 基本信息 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <h3 className="font-semibold">{plugin.name}</h3>
                      <Badge variant={statusCfg.variant}>{statusCfg.label}</Badge>
                      <Badge variant="outline" className="font-mono text-xs">v{plugin.currentVersion}</Badge>
                    </div>
                    <div className="flex flex-wrap gap-4 text-sm text-[hsl(var(--muted-foreground))]">
                      <span>售价：{formatPrice(plugin.price)}</span>
                      <span>下载：{formatNumber(plugin.downloadCount)} 次</span>
                      <span>评分：{plugin.avgRating > 0 ? `${plugin.avgRating.toFixed(1)} ★` : '暂无'}</span>
                      <span>收入：<span className="text-green-600 font-semibold">{formatPrice(plugin.revenue / 100)}</span></span>
                    </div>
                    <p className="text-xs text-[hsl(var(--muted-foreground)/0.6)] mt-1">
                      发布时间：{formatDateTime(plugin.createdAt)}
                    </p>
                  </div>

                  {/* 操作按钮 */}
                  <div className="flex gap-2 shrink-0">
                    <Button size="sm" variant="outline" asChild>
                      <Link href={`/plugins/${plugin.slug}`}>
                        <Eye className="h-3.5 w-3.5" />
                        预览
                      </Link>
                    </Button>
                    <Button size="sm" variant="outline" asChild>
                      <Link href={`/dashboard/plugins/${plugin.id}/edit`}>
                        <Edit className="h-3.5 w-3.5" />
                        编辑
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>
    </div>
  )
}
