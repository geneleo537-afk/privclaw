'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useMemo, useState } from 'react'
import { Download, Search, Package, ExternalLink, Loader2, Star } from 'lucide-react'
import toast from 'react-hot-toast'
import apiClient from '@/lib/api-client'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { usePurchases } from '@/hooks/use-wallet'
import { formatDateTime } from '@/lib/utils'

export default function PurchasesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [downloadingId, setDownloadingId] = useState<string | null>(null)
  const purchasesQuery = usePurchases({ page_size: 100 })

  const filtered = useMemo(() => {
    const items = purchasesQuery.data?.items ?? []
    return items.filter((purchase) => {
      if (!searchQuery) return true
      const keyword = searchQuery.toLowerCase()
      return (
        purchase.pluginName.toLowerCase().includes(keyword) ||
        purchase.pluginSlug.toLowerCase().includes(keyword)
      )
    })
  }, [purchasesQuery.data?.items, searchQuery])

  const handleDownload = async (pluginId: string) => {
    setDownloadingId(pluginId)
    try {
      const res = await apiClient.get(`/plugins/${pluginId}/download`, {
        responseType: 'blob',
      })
      const blob = res.data as Blob
      const disposition = res.headers['content-disposition'] || ''
      const filenameMatch = disposition.match(/filename="?([^"]+)"?/)
      const filename = filenameMatch ? filenameMatch[1] : `${pluginId}.zip`
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      const message = error instanceof Error ? error.message : '下载失败'
      toast.error(message)
    } finally {
      setDownloadingId(null)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">已购插件</h1>
        <p className="text-[hsl(var(--muted-foreground))] text-sm mt-1">
          {purchasesQuery.isLoading
            ? '正在加载已购列表...'
            : `共 ${purchasesQuery.data?.total ?? 0} 个插件，可直接下载当前版本`}
        </p>
      </div>

      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
        <Input
          placeholder="搜索已购插件..."
          className="pl-9"
          value={searchQuery}
          onChange={(event) => setSearchQuery(event.target.value)}
        />
      </div>

      {purchasesQuery.isLoading ? (
        <Card>
          <CardContent className="p-12 text-center text-[hsl(var(--muted-foreground))]">
            正在加载已购插件...
          </CardContent>
        </Card>
      ) : purchasesQuery.isError ? (
        <Card>
          <CardContent className="p-12 text-center text-red-600">
            已购列表加载失败，请检查登录状态或后端服务
          </CardContent>
        </Card>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Package className="h-12 w-12 mx-auto text-[hsl(var(--muted-foreground)/0.4)] mb-3" />
            <p className="text-[hsl(var(--muted-foreground))]">
              {searchQuery ? '未找到匹配的插件' : '还没有购买任何插件'}
            </p>
            {!searchQuery && (
              <Button className="mt-4" variant="outline" asChild>
                <Link href="/plugins">浏览能力库</Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((plugin) => (
            <Card key={plugin.purchaseId} className="hover:shadow-sm transition-shadow">
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-4 flex-1 min-w-0">
                    <div className="h-12 w-12 shrink-0 rounded-xl bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center text-2xl border border-[hsl(var(--border))] overflow-hidden">
                      {plugin.pluginIconUrl ? (
                        <Image
                          src={plugin.pluginIconUrl}
                          alt={plugin.pluginName}
                          width={48}
                          height={48}
                          className="h-full w-full object-cover"
                          unoptimized
                        />
                      ) : (
                        <span>🔌</span>
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <h3 className="font-semibold text-base">{plugin.pluginName}</h3>
                        {plugin.pluginVersion && (
                          <Badge variant="outline" className="font-mono text-xs">
                            v{plugin.pluginVersion}
                          </Badge>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-3 mt-1.5 text-xs text-[hsl(var(--muted-foreground))]">
                        <span>购买时间：{formatDateTime(plugin.purchasedAt)}</span>
                        <span>插件标识：{plugin.pluginSlug}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 shrink-0">
                    <Button
                      size="sm"
                      onClick={() => handleDownload(plugin.pluginId)}
                      disabled={downloadingId === plugin.pluginId}
                    >
                      {downloadingId === plugin.pluginId ? (
                        <>
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          下载中
                        </>
                      ) : (
                        <>
                          <Download className="h-3.5 w-3.5" />
                          下载
                        </>
                      )}
                    </Button>
                    <Button size="sm" variant="ghost" asChild>
                      <Link href={`/plugins/${plugin.pluginSlug}#reviews`}>
                        <Star className="h-3.5 w-3.5" />
                        写评价
                      </Link>
                    </Button>
                    <Button size="sm" variant="ghost" asChild>
                      <Link href={`/plugins/${plugin.pluginSlug}`} target="_blank">
                        <ExternalLink className="h-3.5 w-3.5" />
                        详情
                      </Link>
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
