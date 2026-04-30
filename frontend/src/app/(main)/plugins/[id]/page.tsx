'use client'

import Image from 'next/image'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeft, Download, ShoppingCart, Star, Tag, User } from 'lucide-react'
import toast from 'react-hot-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ReviewList } from '@/components/plugin/review-list'
import { useCreateOrder } from '@/hooks/use-orders'
import { usePlugin, usePluginVersions } from '@/hooks/use-plugins'
import { usePurchases } from '@/hooks/use-wallet'
import { useAuthStore } from '@/stores/auth-store'
import { formatDateTime, formatFileSize, formatNumber, formatPrice } from '@/lib/utils'

export default function PluginDetailPage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const { isAuthenticated } = useAuthStore()
  const identifier = decodeURIComponent(params.id)
  const pluginQuery = usePlugin(identifier)
  const versionsQuery = usePluginVersions(pluginQuery.data?.id)
  const createOrder = useCreateOrder()
  const purchasesQuery = usePurchases({ page_size: 200 })

  const plugin = pluginQuery.data
  const versions = versionsQuery.data ?? []
  const hasPurchased = isAuthenticated
    ? (purchasesQuery.data?.items ?? []).some((p) => p.pluginId === plugin?.id)
    : false

  const handleCreateOrder = async () => {
    if (!plugin) return
    if (!isAuthenticated) {
      router.push('/login')
      return
    }

    try {
      const order = await createOrder.mutateAsync(plugin.id)
      if (order.status === 'paid') {
        toast.success('插件已加入你的已购列表')
        router.push('/dashboard/purchases')
        return
      }
      router.push(`/checkout/${order.id}`)
    } catch (error) {
      const message = error instanceof Error ? error.message : '创建订单失败'
      toast.error(message)
    }
  }

  if (pluginQuery.isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 text-sm text-[hsl(var(--muted-foreground))]">
        插件详情加载中...
      </div>
    )
  }

  if (!plugin) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-sm text-red-600">未找到对应的插件，可能 slug 或 ID 无效。</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <Link
        href="/plugins"
        className="inline-flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] mb-6 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        返回能力库
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          <div className="flex gap-5">
            <div className="h-24 w-24 shrink-0 rounded-2xl bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center text-4xl border border-[hsl(var(--border))] shadow-sm overflow-hidden">
              {plugin.iconUrl ? (
                <Image
                  src={plugin.iconUrl}
                  alt={plugin.name}
                  width={96}
                  height={96}
                  className="h-full w-full object-cover"
                />
              ) : (
                <span>🦞</span>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap items-start gap-2 mb-1">
                <h1 className="text-2xl font-bold">{plugin.name}</h1>
                {plugin.currentVersion && (
                  <Badge variant="secondary">{plugin.currentVersion}</Badge>
                )}
              </div>

              <div className="flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] mb-2">
                <User className="h-3.5 w-3.5" />
                <span>{plugin.developerName}</span>
              </div>

              <div className="flex flex-wrap items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                  <span className="font-medium">{plugin.avgRating.toFixed(1)}</span>
                  <span className="text-[hsl(var(--muted-foreground))]">
                    ({plugin.ratingCount} 条评分)
                  </span>
                </div>
                <div className="flex items-center gap-1 text-[hsl(var(--muted-foreground))]">
                  <Download className="h-3.5 w-3.5" />
                  <span>{formatNumber(plugin.downloadCount)} 次下载</span>
                </div>
                {plugin.categoryName && (
                  <Badge variant="outline">{plugin.categoryName}</Badge>
                )}
              </div>

              <div className="flex flex-wrap gap-1.5 mt-3">
                {plugin.tags.map((tag) => (
                  <Badge key={tag} variant="outline" className="text-xs">
                    <Tag className="h-2.5 w-2.5 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">插件详情</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-[hsl(var(--muted-foreground))] leading-relaxed">
                {plugin.summary}
              </p>
              <div className="whitespace-pre-line text-sm leading-relaxed text-[hsl(var(--foreground))]">
                {plugin.description}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">版本历史</CardTitle>
            </CardHeader>
            <CardContent className="divide-y divide-[hsl(var(--border))]">
              {versionsQuery.isLoading ? (
                <p className="py-4 text-sm text-[hsl(var(--muted-foreground))]">
                  正在加载版本信息...
                </p>
              ) : versions.length === 0 ? (
                <p className="py-4 text-sm text-[hsl(var(--muted-foreground))]">
                  暂无已审核版本
                </p>
              ) : (
                versions.map((version) => (
                  <div key={version.id} className="py-4 first:pt-0 last:pb-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant="outline" className="font-mono text-xs">
                            v{version.version}
                          </Badge>
                          <span className="text-xs text-[hsl(var(--muted-foreground))]">
                            {formatDateTime(version.createdAt)}
                          </span>
                        </div>
                        <p className="text-sm text-[hsl(var(--muted-foreground))]">
                          {version.changelog || '暂无更新日志'}
                        </p>
                      </div>
                      <div className="text-xs text-[hsl(var(--muted-foreground))] shrink-0">
                        {formatFileSize(version.fileSize)}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>

          <ReviewList pluginId={plugin.id} hasPurchased={hasPurchased} />
        </div>

        <div className="lg:col-span-1">
          <div className="sticky top-20 space-y-4">
            <Card className="shadow-md">
              <CardContent className="p-6 space-y-5">
                <div>
                  <p className="text-3xl font-bold text-[hsl(var(--primary))]">
                    {formatPrice(plugin.price)}
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                    {plugin.isFree ? '免费插件，可直接获取' : '下单后进入支付页'}
                  </p>
                </div>

                <Button
                  className="w-full"
                  size="lg"
                  onClick={handleCreateOrder}
                  disabled={createOrder.isPending}
                >
                  <ShoppingCart className="h-4 w-4" />
                  {plugin.isFree ? '免费获取' : `立即购买 ${formatPrice(plugin.price)}`}
                </Button>

                <div className="space-y-2 text-sm text-[hsl(var(--muted-foreground))]">
                  <div className="flex items-center justify-between">
                    <span>插件 ID</span>
                    <span className="font-mono text-xs">{plugin.id.slice(0, 8)}...</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>当前版本</span>
                    <span>{plugin.currentVersion || '未发布'}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>发布时间</span>
                    <span>{plugin.publishedAt ? formatDateTime(plugin.publishedAt) : '未发布'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
