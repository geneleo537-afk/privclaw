'use client'

import { Suspense, useMemo, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Search, SlidersHorizontal, ChevronLeft, ChevronRight } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { PluginGrid } from '@/components/plugin/plugin-grid'
import { usePlugins } from '@/hooks/use-plugins'
import type { PluginCardProps } from '@/components/plugin/plugin-card'

const CATEGORIES = [
  { label: '全部', value: '' },
  { label: '生产力', value: 'productivity' },
  { label: '开发工具', value: 'devtools' },
  { label: 'AI 增强', value: 'ai' },
  { label: '数据分析', value: 'data' },
  { label: '内容创作', value: 'content' },
  { label: '自动化', value: 'automation' },
]

const SORT_OPTIONS = [
  { label: '最新上架', value: 'created_at' },
  { label: '下载最多', value: 'download_count' },
  { label: '评分最高', value: 'avg_rating' },
  { label: '价格最低', value: 'price_asc' },
  { label: '价格最高', value: 'price_desc' },
]

function toCardProps(plugin: {
  id: string
  name: string
  summary: string
  iconUrl?: string
  price: number
  avgRating: number
  downloadCount: number
  developerName: string
  slug: string
}): PluginCardProps {
  return {
    id: plugin.id,
    name: plugin.name,
    description: plugin.summary,
    coverUrl: plugin.iconUrl,
    price: plugin.price,
    avgRating: plugin.avgRating,
    downloadCount: plugin.downloadCount,
    developerName: plugin.developerName,
    slug: plugin.slug,
  }
}

function PluginsContent() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const search = searchParams.get('q') ?? ''
  const category = searchParams.get('category') ?? ''
  const sort = searchParams.get('sort') ?? 'created_at'
  const page = Number(searchParams.get('page') ?? '1')

  const [searchInput, setSearchInput] = useState(search)

  const pluginQuery = usePlugins({
    page,
    page_size: 12,
    search: search || undefined,
    category: category || undefined,
    sort_by: sort,
  })

  const plugins = useMemo(
    () => (pluginQuery.data?.items ?? []).map(toCardProps),
    [pluginQuery.data?.items],
  )
  const total = pluginQuery.data?.total ?? 0
  const totalPages = Math.max(
    1,
    Math.ceil(total / (pluginQuery.data?.page_size || 12)),
  )

  const updateQuery = (updates: Record<string, string | number | undefined>) => {
    const params = new URLSearchParams(searchParams.toString())
    Object.entries(updates).forEach(([key, value]) => {
      if (value === undefined || value === '' || value === 1) {
        params.delete(key)
      } else {
        params.set(key, String(value))
      }
    })
    router.push(`/plugins?${params.toString()}`)
  }

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault()
    updateQuery({
      q: searchInput.trim() || undefined,
      page: undefined,
    })
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">能力库</h1>
        <p className="text-[hsl(var(--muted-foreground))] mt-1">
          浏览全部能力模块，支持搜索、分类与排序。
        </p>
      </div>

      <div className="space-y-4 mb-8">
        <form onSubmit={handleSearch} className="flex gap-3 max-w-xl">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
            <Input
              placeholder="搜索插件名称、功能..."
              className="pl-9"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
            />
          </div>
          <Button type="submit">搜索</Button>
        </form>

        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex items-center gap-1.5">
            <SlidersHorizontal className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
            <span className="text-sm text-[hsl(var(--muted-foreground))]">分类：</span>
          </div>

          <div className="flex flex-wrap gap-1.5">
            {CATEGORIES.map((cat) => (
              <button
                key={cat.value || 'all'}
                onClick={() => updateQuery({ category: cat.value || undefined, page: undefined })}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  category === cat.value
                    ? 'bg-[hsl(var(--primary))] text-white'
                    : 'bg-[hsl(var(--muted)/0.5)] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))]'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex items-center gap-1.5 ml-auto">
            <span className="text-sm text-[hsl(var(--muted-foreground))]">排序：</span>
            <select
              value={sort}
              onChange={(event) => updateQuery({ sort: event.target.value, page: undefined })}
              className="text-sm border border-[hsl(var(--border))] rounded-md px-3 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))]"
            >
              {SORT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {(category || search) && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-[hsl(var(--muted-foreground))]">当前筛选：</span>
            {category && (
              <Badge
                variant="secondary"
                className="gap-1 cursor-pointer"
                onClick={() => updateQuery({ category: undefined, page: undefined })}
              >
                {CATEGORIES.find((item) => item.value === category)?.label ?? category}
                <span>×</span>
              </Badge>
            )}
            {search && (
              <Badge
                variant="secondary"
                className="gap-1 cursor-pointer"
                onClick={() => {
                  setSearchInput('')
                  updateQuery({ q: undefined, page: undefined })
                }}
              >
                {search}
                <span>×</span>
              </Badge>
            )}
          </div>
        )}
      </div>

      <div className="text-sm text-[hsl(var(--muted-foreground))] mb-5">
        {pluginQuery.isLoading ? '正在加载插件...' : `共找到 ${total} 个插件`}
      </div>

      {pluginQuery.isError ? (
        <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-6 text-sm text-red-600">
          插件列表加载失败，请检查后端服务是否已启动。
        </div>
      ) : (
        <PluginGrid plugins={plugins} cols={4} />
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 mt-10">
          <Button
            variant="outline"
            size="sm"
            onClick={() => updateQuery({ page: Math.max(1, page - 1) })}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            上一页
          </Button>

          <div className="flex gap-1">
            {Array.from({ length: totalPages }, (_, index) => index + 1).map((pageNo) => (
              <button
                key={pageNo}
                onClick={() => updateQuery({ page: pageNo })}
                className={`h-8 w-8 rounded-md text-sm font-medium transition-colors ${
                  page === pageNo
                    ? 'bg-[hsl(var(--primary))] text-white'
                    : 'hover:bg-[hsl(var(--muted))]'
                }`}
              >
                {pageNo}
              </button>
            ))}
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => updateQuery({ page: Math.min(totalPages, page + 1) })}
            disabled={page >= totalPages}
          >
            下一页
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  )
}

export default function PluginsPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto px-4 py-8 text-center text-[hsl(var(--muted-foreground))]">
          加载中...
        </div>
      }
    >
      <PluginsContent />
    </Suspense>
  )
}
