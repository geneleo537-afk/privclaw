'use client'

import { useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { ChevronDown, LogOut, Settings, Store, LayoutDashboard, Package, Wallet, BarChart3 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/auth-store'

const sectionMap: Array<{ match: string; label: string; desc: string }> = [
  { match: '/dashboard/orders', label: '订单中心', desc: '查看订单状态、支付情况与购买记录' },
  { match: '/dashboard/purchases', label: '已购插件', desc: '下载你已经购买的插件与版本' },
  { match: '/dashboard/plugins', label: '创作者中心', desc: '管理上架插件、版本与发布信息' },
  { match: '/dashboard/wallet', label: '收益结算', desc: '查看收入、提现记录与资金流水' },
  { match: '/dashboard/settings', label: '账户设置', desc: '维护个人资料、登录信息与账户偏好' },
]

function getWorkspaceSection(pathname: string) {
  return (
    sectionMap.find((item) => pathname.startsWith(item.match)) ?? {
      label: '工作台概览',
      desc: '管理你的订单、插件、收益与账户信息',
    }
  )
}

export function WorkspaceHeader() {
  const pathname = usePathname()
  const router = useRouter()
  const { user, logout } = useAuthStore()
  const [menuOpen, setMenuOpen] = useState(false)

  const section = getWorkspaceSection(pathname)
  const dashboardTarget = '/dashboard'
  const isAdmin = user?.role === 'admin'

  const handleLogout = () => {
    logout()
    setMenuOpen(false)
    router.push('/')
  }

  return (
    <header className="sticky top-0 z-40 border-b border-[hsl(var(--border))] bg-white/96 backdrop-blur">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between gap-4">
          <div className="flex items-center gap-4 min-w-0">
            <Link href="/" className="flex items-center gap-2 shrink-0">
              <span className="text-2xl">🦞</span>
              <div className="leading-tight">
                <p className="font-bold text-[hsl(var(--primary))]">PrivClaw</p>
                <p className="text-[11px] text-[hsl(var(--muted-foreground))]">Workspace</p>
              </div>
            </Link>

            <div className="hidden md:block h-8 w-px bg-[hsl(var(--border))]" />

            <div className="hidden md:block min-w-0">
              <p className="text-sm font-semibold truncate">{section.label}</p>
              <p className="text-xs text-[hsl(var(--muted-foreground))] truncate">
                {section.desc}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" asChild>
              <Link href="/plugins">
                <Store className="h-4 w-4" />
                浏览能力库
              </Link>
            </Button>

            <div className="relative">
              <button
                onClick={() => setMenuOpen((value) => !value)}
                className="flex items-center gap-2 rounded-full border border-[hsl(var(--border))] px-3 py-1.5 hover:bg-[hsl(var(--accent))] transition-colors"
              >
                <div className="h-8 w-8 rounded-full bg-[hsl(var(--primary)/0.14)] flex items-center justify-center text-[hsl(var(--primary))] font-semibold text-sm">
                  {user?.nickname?.charAt(0).toUpperCase() || 'U'}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium leading-none">{user?.nickname || '用户'}</p>
                  <p className="text-[11px] text-[hsl(var(--muted-foreground))] mt-1">
                    {user?.role === 'admin' ? '管理员' : user?.role === 'developer' ? '开发者' : '买家'}
                  </p>
                </div>
                <ChevronDown className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
              </button>

              {menuOpen && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setMenuOpen(false)} />
                  <div className="absolute right-0 top-full mt-2 z-50 w-56 rounded-2xl border border-[hsl(var(--border))] bg-white shadow-lg py-2">
                    <div className="px-4 py-2 border-b border-[hsl(var(--border))]">
                      <p className="text-sm font-medium">{user?.nickname}</p>
                      <p className="text-xs text-[hsl(var(--muted-foreground))] truncate">{user?.email}</p>
                    </div>
                    <Link
                      href={dashboardTarget}
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))]"
                    >
                      <LayoutDashboard className="h-4 w-4" />
                      工作台首页
                    </Link>
                    {isAdmin && (
                      <Link
                        href="/admin"
                        onClick={() => setMenuOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))]"
                      >
                        <BarChart3 className="h-4 w-4" />
                        管理后台
                      </Link>
                    )}
                    <Link
                      href="/dashboard/purchases"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))]"
                    >
                      <Package className="h-4 w-4" />
                      已购插件
                    </Link>
                    <Link
                      href="/dashboard/wallet"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))]"
                    >
                      <Wallet className="h-4 w-4" />
                      我的钱包
                    </Link>
                    <Link
                      href="/dashboard/settings"
                      onClick={() => setMenuOpen(false)}
                      className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))]"
                    >
                      <Settings className="h-4 w-4" />
                      账户设置
                    </Link>
                    <div className="my-1 border-t border-[hsl(var(--border))]" />
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      <LogOut className="h-4 w-4" />
                      退出登录
                    </button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
