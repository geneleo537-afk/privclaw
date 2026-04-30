'use client'

import { useState } from 'react'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Search,
  Menu,
  X,
  ChevronDown,
  LogOut,
  Settings,
  LayoutDashboard,
  Package,
  Lightbulb,
  Blocks,
  Info,
  MessageCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/stores/auth-store'

const MAIN_NAV = [
  { label: '服务方案', href: '/#solutions', icon: Lightbulb },
  { label: '能力库', href: '/plugins', icon: Blocks },
  { label: '关于我们', href: '/about', icon: Info },
  { label: '免费咨询', href: '/contact', icon: MessageCircle },
]

export function Header() {
  const router = useRouter()
  const { user, isAuthenticated, logout } = useAuthStore()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (searchQuery.trim()) {
      router.push(`/plugins?q=${encodeURIComponent(searchQuery.trim())}`)
      setMobileOpen(false)
    }
  }

  const handleLogout = () => {
    logout()
    setUserMenuOpen(false)
    router.push('/')
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b border-[hsl(var(--border))] bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-2.5 shrink-0">
            <span className="text-4xl">🦞</span>
            <div className="hidden sm:block leading-tight">
              <span className="font-black text-2xl block" style={{ color: '#EB4C4C' }}>
                PrivClaw
              </span>
              <span className="text-xs text-[hsl(var(--muted-foreground))] block">
                智慧龙虾定制
              </span>
            </div>
          </Link>

          <form onSubmit={handleSearch} className="hidden md:flex flex-1 max-w-xl">
            <div className="relative w-full">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
              <Input
                type="search"
                placeholder="搜索能力模块、解决方案..."
                className="pl-9 rounded-full border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.5)] focus-visible:bg-white"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </form>

          <div className="hidden md:flex items-center gap-2">
            <nav className="flex items-center gap-1">
              {MAIN_NAV.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="px-3 py-2 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] transition-colors rounded-md hover:bg-[hsl(var(--accent))]"
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            {isAuthenticated && user ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 rounded-full px-3 py-1.5 hover:bg-[hsl(var(--accent))] transition-colors"
                >
                  <div className="h-8 w-8 rounded-full bg-[hsl(var(--primary)/0.15)] flex items-center justify-center text-[hsl(var(--primary))] font-semibold text-sm">
                    {user.avatarUrl ? (
                      <Image
                        src={user.avatarUrl}
                        alt={user.nickname}
                        width={32}
                        height={32}
                        className="h-8 w-8 rounded-full object-cover"
                      />
                    ) : (
                      user.nickname.charAt(0).toUpperCase()
                    )}
                  </div>
                  <span className="text-sm font-medium">{user.nickname}</span>
                  <ChevronDown className="h-3.5 w-3.5 text-[hsl(var(--muted-foreground))]" />
                </button>

                {userMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setUserMenuOpen(false)}
                    />
                    <div className="absolute right-0 top-full mt-1 z-50 w-52 rounded-xl border border-[hsl(var(--border))] bg-white shadow-lg py-1">
                      <div className="px-4 py-2 border-b border-[hsl(var(--border))]">
                        <p className="text-sm font-medium">{user.nickname}</p>
                        <p className="text-xs text-[hsl(var(--muted-foreground))] truncate">{user.email}</p>
                      </div>
                      <Link
                        href="/dashboard"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))] transition-colors"
                      >
                        <LayoutDashboard className="h-4 w-4" />
                        控制台
                      </Link>
                      <Link
                        href="/dashboard/purchases"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))] transition-colors"
                      >
                        <Package className="h-4 w-4" />
                        已购插件
                      </Link>
                      <Link
                        href="/dashboard/settings"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--accent))] transition-colors"
                      >
                        <Settings className="h-4 w-4" />
                        账户设置
                      </Link>
                      <hr className="my-1 border-[hsl(var(--border))]" />
                      <button
                        onClick={handleLogout}
                        className="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <LogOut className="h-4 w-4" />
                        退出登录
                      </button>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" asChild>
                  <Link href="/login">登录</Link>
                </Button>
                <Button size="sm" asChild style={{ backgroundColor: '#EB4C4C' }} className="border-0 hover:opacity-90 transition-opacity text-white">
                  <Link href="/register">免费注册</Link>
                </Button>
              </div>
            )}
          </div>

          {/* 移动端汉堡菜单按钮 */}
          <button
            className="md:hidden p-2 rounded-md hover:bg-[hsl(var(--accent))] transition-colors"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="切换菜单"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {mobileOpen && (
          <div className="md:hidden border-t border-[hsl(var(--border))] py-4 space-y-4">
            <form onSubmit={handleSearch} className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[hsl(var(--muted-foreground))]" />
                <Input
                  type="search"
                  placeholder="搜索能力模块、解决方案..."
                  className="pl-9"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Button type="submit" size="sm">搜索</Button>
            </form>

            <div className="grid grid-cols-1 gap-2">
              {MAIN_NAV.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center justify-between px-3 py-2 text-sm rounded-lg bg-[hsl(var(--muted)/0.5)] hover:bg-[hsl(var(--accent))] transition-colors"
                >
                  <span>{item.label}</span>
                  <item.icon className="h-4 w-4" />
                </Link>
              ))}
            </div>

            {isAuthenticated && user ? (
              <div className="space-y-1 border-t border-[hsl(var(--border))] pt-4">
                <p className="px-2 text-sm font-medium text-[hsl(var(--muted-foreground))]">
                  {user.nickname}
                </p>
                <Link
                  href="/dashboard"
                  onClick={() => setMobileOpen(false)}
                  className="flex items-center gap-2 px-2 py-2 text-sm rounded-lg hover:bg-[hsl(var(--accent))]"
                >
                  <LayoutDashboard className="h-4 w-4" />
                  控制台
                </Link>
                <button
                  onClick={handleLogout}
                  className="flex w-full items-center gap-2 px-2 py-2 text-sm text-red-600 rounded-lg hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4" />
                  退出登录
                </button>
              </div>
            ) : (
              <div className="flex gap-2 border-t border-[hsl(var(--border))] pt-4">
                <Button variant="outline" className="flex-1" asChild>
                  <Link href="/login" onClick={() => setMobileOpen(false)}>登录</Link>
                </Button>
                <Button className="flex-1" asChild>
                  <Link href="/register" onClick={() => setMobileOpen(false)}>注册</Link>
                </Button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  )
}
