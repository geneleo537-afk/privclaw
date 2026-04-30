'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Sidebar } from '@/components/layout/sidebar'
import { WorkspaceHeader } from '@/components/layout/workspace-header'
import { useAuthStore } from '@/stores/auth-store'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()
  const { hasHydrated, isAuthenticated } = useAuthStore()

  useEffect(() => {
    if (hasHydrated && !isAuthenticated) {
      router.replace('/login')
    }
  }, [hasHydrated, isAuthenticated, router])

  if (!hasHydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-[hsl(var(--muted-foreground))]">正在恢复登录状态...</p>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-3">
          <span className="text-5xl">🦞</span>
          <p className="text-[hsl(var(--muted-foreground))]">请先登录...</p>
          <Link href="/login" className="text-sm text-[hsl(var(--primary))] hover:underline">
            前往登录
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col">
      <WorkspaceHeader />
      <div className="container mx-auto px-4 py-6 md:py-8 flex flex-col md:flex-row gap-4 md:gap-8 flex-1">
        <Sidebar />
        <main className="flex-1 min-w-0">{children}</main>
      </div>
    </div>
  )
}
