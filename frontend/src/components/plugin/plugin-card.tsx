import Link from 'next/link'
import Image from 'next/image'
import { Star, Download, User } from 'lucide-react'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatPrice, formatNumber } from '@/lib/utils'

export interface PluginCardProps {
  id: string
  name: string
  description: string
  coverUrl?: string
  price: number
  avgRating: number
  downloadCount: number
  developerName: string
  slug: string
}

export function PluginCard({
  id,
  name,
  description,
  coverUrl,
  price,
  avgRating,
  downloadCount,
  developerName,
  slug,
}: PluginCardProps) {
  return (
    <Link href={`/plugins/${slug || id}`} className="group block">
      <Card className="h-full overflow-hidden transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 hover:border-[hsl(var(--primary)/0.3)]">
        {/* 封面图 */}
        <div className="relative aspect-video w-full overflow-hidden bg-gradient-to-br from-orange-50 to-red-50">
          {coverUrl ? (
            <Image
              src={coverUrl}
              alt={name}
              fill
              className="object-cover transition-transform duration-300 group-hover:scale-105"
              sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
            />
          ) : (
            <div className="flex h-full items-center justify-center">
              <span className="text-5xl">🦞</span>
            </div>
          )}
          {/* 价格标签 */}
          <div className="absolute right-2 top-2">
            <Badge
              className={
                price === 0
                  ? 'bg-green-500 text-white border-0'
                  : 'bg-[hsl(var(--primary))] text-white border-0'
              }
            >
              {formatPrice(price)}
            </Badge>
          </div>
        </div>

        <CardContent className="p-4">
          {/* 插件名称 */}
          <h3 className="font-semibold text-base leading-tight line-clamp-1 group-hover:text-[hsl(var(--primary))] transition-colors">
            {name}
          </h3>

          {/* 开发者 */}
          <div className="mt-1 flex items-center gap-1 text-xs text-[hsl(var(--muted-foreground))]">
            <User className="h-3 w-3" />
            <span className="line-clamp-1">{developerName}</span>
          </div>

          {/* 简介 */}
          <p className="mt-2 text-sm text-[hsl(var(--muted-foreground))] line-clamp-2 leading-relaxed">
            {description}
          </p>
        </CardContent>

        <CardFooter className="px-4 pb-4 pt-0">
          {/* 评分 + 下载量 */}
          <div className="flex w-full items-center justify-between text-xs text-[hsl(var(--muted-foreground))]">
            <div className="flex items-center gap-1">
              <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
              <span className="font-medium text-[hsl(var(--foreground))]">
                {avgRating > 0 ? avgRating.toFixed(1) : '暂无'}
              </span>
            </div>
            <div className="flex items-center gap-1">
              <Download className="h-3.5 w-3.5" />
              <span>{formatNumber(downloadCount)} 次下载</span>
            </div>
          </div>
        </CardFooter>
      </Card>
    </Link>
  )
}
