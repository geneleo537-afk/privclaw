'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  ShoppingBag,
  Package,
  Code2,
  Wallet,
  Settings,
  BarChart3,
  Users,
  ClipboardCheck,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuthStore } from '@/stores/auth-store'

interface NavItem {
  label: string
  href: string
  icon: typeof LayoutDashboard
  roles: string[]
  section?: string
}

const baseNavItems: NavItem[] = [
  {
    label: '概览',
    href: '/dashboard',
    icon: LayoutDashboard,
    roles: ['user', 'developer', 'admin'],
  },
  {
    label: '我的订单',
    href: '/dashboard/orders',
    icon: ShoppingBag,
    roles: ['user', 'developer', 'admin'],
  },
  {
    label: '已购插件',
    href: '/dashboard/purchases',
    icon: Package,
    roles: ['user', 'developer', 'admin'],
  },
  {
    label: '我的插件',
    href: '/dashboard/plugins',
    icon: Code2,
    roles: ['developer', 'admin'],
  },
  {
    label: '我的钱包',
    href: '/dashboard/wallet',
    icon: Wallet,
    roles: ['developer', 'admin'],
  },
  {
    label: '账户设置',
    href: '/dashboard/settings',
    icon: Settings,
    roles: ['user', 'developer', 'admin'],
  },
  // ─── 管理后台（仅 admin）─────────────────
  {
    label: '数据大盘',
    href: '/admin',
    icon: BarChart3,
    roles: ['admin'],
    section: 'admin',
  },
  {
    label: '插件管理',
    href: '/admin/plugins',
    icon: Package,
    roles: ['admin'],
    section: 'admin',
  },
  {
    label: '订单管理',
    href: '/admin/orders',
    icon: ShoppingBag,
    roles: ['admin'],
    section: 'admin',
  },
  {
    label: '提现审批',
    href: '/admin/withdrawals',
    icon: ClipboardCheck,
    roles: ['admin'],
    section: 'admin',
  },
  {
    label: '用户管理',
    href: '/admin/users',
    icon: Users,
    roles: ['admin'],
    section: 'admin',
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { user } = useAuthStore()
  const userRole = user?.role ?? 'user'

  const navItems = baseNavItems.filter((item) =>
    item.roles.includes(userRole),
  )
  const userItems = navItems.filter((item) => !('section' in item && item.section === 'admin'))
  const adminItems = navItems.filter((item) => 'section' in item && item.section === 'admin')

  const renderItem = (item: NavItem) => {
    const Icon = item.icon
    const isActive =
      item.href === '/dashboard'
        ? pathname === '/dashboard'
        : item.href === '/admin'
          ? pathname === '/admin'
          : pathname.startsWith(item.href)

    return (
      <Link
        key={item.href}
        href={item.href}
        className={cn(
          'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
          isActive
            ? 'bg-[hsl(var(--primary)/0.1)] text-[hsl(var(--primary))]'
            : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted)/0.5)] hover:text-[hsl(var(--foreground))]',
        )}
      >
        <Icon
          className={cn(
            'h-4 w-4 shrink-0',
            isActive ? 'text-[hsl(var(--primary))]' : '',
          )}
        />
        {item.label}
        {isActive && (
          <span className="ml-auto h-1.5 w-1.5 rounded-full bg-[hsl(var(--primary))]" />
        )}
      </Link>
    )
  }

  return (
    <aside className="w-60 shrink-0 hidden md:block">
      <nav className="sticky top-20 flex flex-col gap-1">
        {userItems.map(renderItem)}
        {adminItems.length > 0 && (
          <>
            <div className="mt-4 mb-1 px-3 text-[11px] font-semibold uppercase tracking-wider text-[hsl(var(--muted-foreground)/0.6)]">
              管理后台
            </div>
            {adminItems.map(renderItem)}
          </>
        )}
      </nav>
    </aside>
  )
}
