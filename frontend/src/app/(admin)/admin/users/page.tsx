'use client'
import { useState } from 'react'
import { DataTable } from '@/components/common/data-table'
import { StatusBadge } from '@/components/common/status-badge'
import { Pagination } from '@/components/common/pagination'
import { Button } from '@/components/ui/button'

interface AdminUser {
  id: string
  nickname: string
  email: string
  role: string
  status: string
  registered_at: string
}

const ROLE_MAP: Record<string, string> = {
  admin: '管理员',
  developer: '开发者',
  user: '普通用户',
}

const mockUsers: AdminUser[] = [
  {
    id: 'u001',
    nickname: '张开发',
    email: 'dev_zhang@example.com',
    role: 'developer',
    status: 'active',
    registered_at: '2026-01-15',
  },
  {
    id: 'u002',
    nickname: '李程序',
    email: 'li_coder@example.com',
    role: 'developer',
    status: 'active',
    registered_at: '2026-01-20',
  },
  {
    id: 'u003',
    nickname: '普通用户小王',
    email: 'wang@example.com',
    role: 'user',
    status: 'active',
    registered_at: '2026-02-01',
  },
  {
    id: 'u004',
    nickname: '违规账号',
    email: 'spam@example.com',
    role: 'user',
    status: 'banned',
    registered_at: '2026-02-10',
  },
  {
    id: 'u005',
    nickname: '超级管理员',
    email: 'admin@lobster.shop',
    role: 'admin',
    status: 'active',
    registered_at: '2026-01-01',
  },
]

type UserRow = Record<string, unknown> & AdminUser

export default function AdminUsersPage() {
  const [page, setPage] = useState(1)

  const columns = [
    { key: 'id', header: '用户ID', className: 'font-mono text-xs text-gray-500' },
    { key: 'nickname', header: '昵称', className: 'font-medium' },
    { key: 'email', header: '邮箱', className: 'text-gray-600' },
    {
      key: 'role',
      header: '角色',
      render: (row: UserRow) => (
        <span className="text-sm">{ROLE_MAP[row.role as string] ?? (row.role as string)}</span>
      ),
    },
    {
      key: 'status',
      header: '状态',
      render: (row: UserRow) => <StatusBadge status={row.status as string} />,
    },
    { key: 'registered_at', header: '注册时间' },
    {
      key: 'actions',
      header: '操作',
      render: (row: UserRow) =>
        row.role === 'admin' ? (
          <span className="text-xs text-gray-400">超级管理员</span>
        ) : row.status === 'active' ? (
          <Button
            size="sm"
            variant="outline"
            className="text-red-600 border-red-200 hover:bg-red-50"
          >
            封禁
          </Button>
        ) : (
          <Button
            size="sm"
            variant="outline"
            className="text-green-600 border-green-200 hover:bg-green-50"
          >
            解封
          </Button>
        ),
    },
  ]

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">用户管理</h1>
          <p className="text-sm text-gray-500 mt-1">管理平台所有注册用户</p>
        </div>
        <div className="text-sm text-gray-500">
          共 <span className="font-semibold text-gray-900">{mockUsers.length}</span> 名用户
        </div>
      </div>

      {/* 桌面端表格 */}
      <div className="hidden md:block bg-white rounded-xl shadow-sm border overflow-hidden">
        <DataTable
          columns={columns as Parameters<typeof DataTable>[0]['columns']}
          data={mockUsers as UserRow[]}
        />
        <div className="p-4">
          <Pagination page={page} total={mockUsers.length} pageSize={10} onPageChange={setPage} />
        </div>
      </div>

      {/* 移动端卡片 */}
      <div className="md:hidden space-y-3">
        {mockUsers.map((u) => (
          <div key={u.id} className="bg-white rounded-xl shadow-sm border p-4 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-medium">{u.nickname}</span>
              <StatusBadge status={u.status} />
            </div>
            <p className="text-sm text-gray-600 truncate">{u.email}</p>
            <div className="flex items-center justify-between text-xs text-gray-400">
              <span>{ROLE_MAP[u.role] ?? u.role}</span>
              <span>{u.registered_at}</span>
            </div>
            {u.role !== 'admin' && (
              u.status === 'active' ? (
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full text-red-600 border-red-200 hover:bg-red-50"
                >
                  封禁
                </Button>
              ) : (
                <Button
                  size="sm"
                  variant="outline"
                  className="w-full text-green-600 border-green-200 hover:bg-green-50"
                >
                  解封
                </Button>
              )
            )}
          </div>
        ))}
        <div className="py-2">
          <Pagination page={page} total={mockUsers.length} pageSize={10} onPageChange={setPage} />
        </div>
      </div>
    </div>
  )
}
