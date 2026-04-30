'use client'

import { useState } from 'react'
import { ArrowDownToLine, Loader2, TrendingUp, Wallet, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { useWallet, useWalletTransactions, useWithdraw } from '@/hooks/use-wallet'
import { formatDateTime, formatPrice } from '@/lib/utils'

const TYPE_CONFIG: Record<string, { label: string; color: string }> = {
  settlement: { label: '销售收益', color: 'text-green-600' },
  withdrawal: { label: '提现', color: 'text-[hsl(var(--primary))]' },
  refund: { label: '退款', color: 'text-red-500' },
  payment: { label: '余额支付', color: 'text-blue-600' },
  platform_fee: { label: '平台手续费', color: 'text-[hsl(var(--muted-foreground))]' },
}

const STATUS_MAP: Record<string, { label: string; variant: 'success' | 'warning' | 'destructive' }> = {
  completed: { label: '已完成', variant: 'success' },
  pending: { label: '处理中', variant: 'warning' },
  failed: { label: '失败', variant: 'destructive' },
}

export default function WalletPage() {
  const walletQuery = useWallet()
  const transactionsQuery = useWalletTransactions({ page_size: 50 })
  const withdrawMutation = useWithdraw()

  const [withdrawAmount, setWithdrawAmount] = useState('')
  const [alipayAccount, setAlipayAccount] = useState('')
  const [realName, setRealName] = useState('')

  const balance = walletQuery.data
  const transactions = transactionsQuery.data?.items ?? []

  const totalPending = 0

  const handleWithdraw = async (event: React.FormEvent) => {
    event.preventDefault()
    const amount = Number(withdrawAmount)
    if (!Number.isFinite(amount) || amount < 100) {
      toast.error('提现金额至少 ¥100')
      return
    }
    if ((balance?.balance ?? 0) < amount) {
      toast.error('提现金额不能超过可用余额')
      return
    }
    if (!alipayAccount.trim()) {
      toast.error('请填写支付宝账号')
      return
    }
    if (!realName.trim()) {
      toast.error('请填写真实姓名')
      return
    }

    try {
      await withdrawMutation.mutateAsync({
        amount,
        alipay_account: alipayAccount.trim(),
        alipay_name: realName.trim(),
      })
      toast.success('提现申请已提交')
      setWithdrawAmount('')
      setAlipayAccount('')
      setRealName('')
    } catch (error) {
      const message = error instanceof Error ? error.message : '提现申请失败'
      toast.error(message)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">我的钱包</h1>
        <p className="text-[hsl(var(--muted-foreground))] text-sm mt-1">
          管理收益与提现
        </p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            label: '可用余额',
            value: balance?.balance ?? 0,
            icon: Wallet,
            color: 'text-[hsl(var(--primary))]',
            bg: 'bg-orange-50',
          },
          {
            label: '冻结金额',
            value: totalPending,
            icon: Clock,
            color: 'text-amber-500',
            bg: 'bg-amber-50',
          },
          {
            label: '累计收入',
            value: balance?.totalEarned ?? 0,
            icon: TrendingUp,
            color: 'text-green-600',
            bg: 'bg-green-50',
          },
          {
            label: '已提现',
            value: balance?.totalWithdrawn ?? 0,
            icon: ArrowDownToLine,
            color: 'text-blue-600',
            bg: 'bg-blue-50',
          },
        ].map((item) => {
          const Icon = item.icon
          return (
            <Card key={item.label}>
              <CardContent className="p-4">
                <div className={`inline-flex h-9 w-9 items-center justify-center rounded-lg ${item.bg} mb-3`}>
                  <Icon className={`h-4.5 w-4.5 ${item.color}`} />
                </div>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mb-1">
                  {item.label}
                </p>
                <p className={`text-xl font-bold ${item.color}`}>
                  {formatPrice(item.value)}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <ArrowDownToLine className="h-4 w-4" />
              申请提现
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleWithdraw} className="space-y-4">
              <div className="rounded-lg bg-[hsl(var(--muted)/0.5)] px-4 py-3 text-sm">
                <span className="text-[hsl(var(--muted-foreground))]">可提现金额：</span>
                <span className="font-bold text-[hsl(var(--primary))]">
                  {formatPrice(balance?.balance ?? 0)}
                </span>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">提现金额（元）</label>
                <div className="flex">
                  <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.5)] text-sm text-[hsl(var(--muted-foreground))]">
                    ¥
                  </span>
                  <Input
                    type="number"
                    className="rounded-l-none"
                    placeholder="最低 ¥100"
                    value={withdrawAmount}
                    onChange={(event) => setWithdrawAmount(event.target.value)}
                    min="100"
                    max={balance?.balance ?? 0}
                    step="1"
                    disabled={withdrawMutation.isPending}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">支付宝账号</label>
                <Input
                  placeholder="手机号或邮箱"
                  value={alipayAccount}
                  onChange={(event) => setAlipayAccount(event.target.value)}
                  disabled={withdrawMutation.isPending}
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-sm font-medium">真实姓名</label>
                <Input
                  placeholder="与支付宝实名一致"
                  value={realName}
                  onChange={(event) => setRealName(event.target.value)}
                  disabled={withdrawMutation.isPending}
                />
              </div>

              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                当前本地环境已接真实提现接口，最低提现金额按后端规则为 ¥100。
              </p>

              <Button type="submit" className="w-full" disabled={withdrawMutation.isPending}>
                {withdrawMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    提交中...
                  </>
                ) : (
                  '申请提现'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">收支流水</CardTitle>
          </CardHeader>
          <CardContent className="divide-y divide-[hsl(var(--border))]">
            {transactionsQuery.isLoading ? (
              <p className="py-4 text-sm text-[hsl(var(--muted-foreground))]">
                正在加载流水...
              </p>
            ) : transactions.length === 0 ? (
              <p className="py-4 text-sm text-[hsl(var(--muted-foreground))]">
                暂无流水记录
              </p>
            ) : (
              transactions.map((tx) => {
                const typeInfo = TYPE_CONFIG[tx.type] ?? {
                  label: tx.type,
                  color: 'text-[hsl(var(--muted-foreground))]',
                }
                const statusInfo = STATUS_MAP.completed
                const signedAmount = tx.direction === 'in' ? tx.amount : -tx.amount

                return (
                  <div key={tx.id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-sm font-medium truncate">{tx.description}</span>
                        <Badge variant={statusInfo.variant} className="shrink-0 text-xs py-0">
                          {statusInfo.label}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-[hsl(var(--muted-foreground))]">
                        <span className={typeInfo.color}>{typeInfo.label}</span>
                        <span>·</span>
                        <span>{formatDateTime(tx.createdAt)}</span>
                      </div>
                    </div>
                    <span
                      className={`ml-4 text-sm font-semibold shrink-0 ${
                        signedAmount > 0 ? 'text-green-600' : 'text-[hsl(var(--muted-foreground))]'
                      }`}
                    >
                      {signedAmount > 0 ? '+' : ''}
                      {formatPrice(signedAmount)}
                    </span>
                  </div>
                )
              })
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
