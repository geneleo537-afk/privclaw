import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-orange-50/50 to-white px-4">
      <div className="text-center">
        <span className="text-8xl block mb-6">🦞</span>
        <h1 className="text-8xl font-bold text-[hsl(var(--primary)/0.2)] mb-2 leading-none">404</h1>
        <h2 className="text-2xl font-bold mb-3">页面不见了</h2>
        <p className="text-[hsl(var(--muted-foreground))] mb-8 max-w-sm mx-auto">
          这只龙虾已经游走了，你要找的页面可能已被删除、移动或从未存在过。
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Button asChild>
            <Link href="/">返回首页</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/#solutions">了解服务</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
