'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Sidebar } from '@/components/layout/sidebar'
import { WorkspaceHeader } from '@/components/layout/workspace-header'
import { useAuthStore } from '@/stores/auth-store'

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, hasHydrated } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (hasHydrated && (!isAuthenticated || user?.role !== 'admin')) {
      router.replace('/login')
    }
  }, [hasHydrated, isAuthenticated, user, router])

  if (!hasHydrated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-[hsl(var(--muted-foreground))]">正在恢复登录状态...</p>
      </div>
    )
  }

  if (!isAuthenticated || user?.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-[hsl(var(--muted-foreground))]">正在跳转到登录页...</p>
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
