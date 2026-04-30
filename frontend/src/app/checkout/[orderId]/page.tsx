'use client'

import { useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import {
  AlertCircle,
  ArrowLeft,
  CheckCircle,
  Clock,
  CreditCard,
  ExternalLink,
  Loader2,
  Wallet,
} from 'lucide-react'
import toast from 'react-hot-toast'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  useDevCompletePayment,
  useOrder,
  useOrderStatus,
  usePayWithAlipay,
  usePayWithBalance,
} from '@/hooks/use-orders'
import { formatPrice } from '@/lib/utils'

type PayChannel = 'alipay' | 'balance'

export default function CheckoutPage() {
  const router = useRouter()
  const params = useParams<{ orderId: string }>()
  const orderId = params.orderId

  const [selectedChannel, setSelectedChannel] = useState<PayChannel>('alipay')
  const [pollingEnabled, setPollingEnabled] = useState(false)
  const [paymentLink, setPaymentLink] = useState('')
  const [now, setNow] = useState(Date.now())

  const orderQuery = useOrder(orderId)
  const statusQuery = useOrderStatus(orderId, pollingEnabled)
  const payWithAlipay = usePayWithAlipay()
  const payWithBalance = usePayWithBalance()
  const devCompletePayment = useDevCompletePayment()

  const order = orderQuery.data
  const orderStatus = statusQuery.data?.status ?? order?.status

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), 1000)
    return () => window.clearInterval(timer)
  }, [])

  useEffect(() => {
    if (orderStatus === 'paid') {
      setPollingEnabled(false)
      toast.success('支付成功，正在跳转到已购插件')
      const timer = window.setTimeout(() => {
        router.push('/dashboard/purchases')
      }, 1200)
      return () => window.clearTimeout(timer)
    }
    return undefined
  }, [orderStatus, router])

  const timeLeft = useMemo(() => {
    if (!order?.expiresAt) return 0
    return Math.max(0, Math.floor((new Date(order.expiresAt).getTime() - now) / 1000))
  }, [now, order?.expiresAt])

  const formatCountdown = (seconds: number) => {
    const minutes = Math.floor(seconds / 60)
    const remainder = seconds % 60
    return `${minutes.toString().padStart(2, '0')}:${remainder.toString().padStart(2, '0')}`
  }

  const handleCreatePayment = async () => {
    if (!order) return

    try {
      if (selectedChannel === 'balance') {
        await payWithBalance.mutateAsync(order.id)
        toast.success('余额支付成功')
        router.push('/dashboard/purchases')
        return
      }

      const session = await payWithAlipay.mutateAsync(order.id)
      setPaymentLink(session.qrCodeUrl)
      setPollingEnabled(true)
      toast.success('已生成支付宝支付链接')
    } catch (error) {
      const message = error instanceof Error ? error.message : '发起支付失败'
      toast.error(message)
    }
  }

  const handleDevComplete = async () => {
    if (!order) return
    try {
      await devCompletePayment.mutateAsync(order.id)
      setPollingEnabled(false)
      toast.success('本地模拟支付成功')
      router.push('/dashboard/purchases')
    } catch (error) {
      const message = error instanceof Error ? error.message : '模拟支付失败'
      toast.error(message)
    }
  }

  if (orderQuery.isLoading) {
    return (
      <div className="container mx-auto max-w-lg px-4 py-10 text-sm text-[hsl(var(--muted-foreground))]">
        订单信息加载中...
      </div>
    )
  }

  if (!order) {
    return (
      <div className="container mx-auto max-w-lg px-4 py-10">
        <p className="text-sm text-red-600">未找到该订单，请返回插件详情重新下单。</p>
      </div>
    )
  }

  const isPaid = orderStatus === 'paid'
  const isExpired = orderStatus === 'closed' || timeLeft === 0

  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50/50 to-white">
      <div className="container mx-auto max-w-lg px-4 py-10">
        <button
          onClick={() => router.back()}
          className="flex items-center gap-1.5 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] mb-8 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          返回
        </button>

        <h1 className="text-2xl font-bold mb-6 text-center">订单支付</h1>

        {isPaid && (
          <Card className="text-center py-10 border-green-200 bg-green-50">
            <CardContent>
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-green-700 mb-2">支付成功</h2>
              <p className="text-green-600 text-sm">正在跳转到已购插件页面...</p>
            </CardContent>
          </Card>
        )}

        {isExpired && !isPaid && (
          <Card className="text-center py-10 border-red-100 bg-red-50">
            <CardContent>
              <AlertCircle className="h-16 w-16 text-red-400 mx-auto mb-4" />
              <h2 className="text-xl font-bold text-red-600 mb-2">订单已超时</h2>
              <p className="text-[hsl(var(--muted-foreground))] text-sm mb-6">
                当前订单已失效，请返回详情页重新下单。
              </p>
              <Button variant="outline" asChild>
                <Link href={`/plugins/${order.pluginSnapshot.id || ''}`}>
                  返回插件详情
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}

        {!isPaid && !isExpired && (
          <div className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">订单信息</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-[hsl(var(--muted-foreground))]">订单号</span>
                  <span className="font-mono font-medium">{order.orderNo}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-[hsl(var(--muted-foreground))]">插件名称</span>
                  <span className="font-medium">{order.pluginSnapshot.name}</span>
                </div>
                <div className="flex justify-between items-center border-t border-[hsl(var(--border))] pt-3 mt-3">
                  <span className="font-semibold">应付金额</span>
                  <span className="text-2xl font-bold text-[hsl(var(--primary))]">
                    {formatPrice(order.paidAmount)}
                  </span>
                </div>

                <div className="flex items-center justify-center gap-2 bg-amber-50 rounded-lg py-2 mt-1">
                  <Clock className="h-4 w-4 text-amber-500" />
                  <span className="text-sm text-amber-600">
                    订单将在 <span className="font-bold font-mono">{formatCountdown(timeLeft)}</span> 后失效
                  </span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">选择支付方式</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {[
                  {
                    channel: 'alipay' as PayChannel,
                    icon: <CreditCard className="h-5 w-5 text-blue-500" />,
                    label: '支付宝',
                    desc: '生成支付链接，完成沙箱或正式支付',
                  },
                  {
                    channel: 'balance' as PayChannel,
                    icon: <Wallet className="h-5 w-5 text-[hsl(var(--primary))]" />,
                    label: '余额支付',
                    desc: '适合本地联调开发者钱包流程',
                  },
                ].map((item) => (
                  <label
                    key={item.channel}
                    className={`flex items-center gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all ${
                      selectedChannel === item.channel
                        ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary)/0.04)]'
                        : 'border-[hsl(var(--border))] hover:border-[hsl(var(--primary)/0.3)]'
                    }`}
                  >
                    <input
                      type="radio"
                      name="payChannel"
                      value={item.channel}
                      checked={selectedChannel === item.channel}
                      onChange={() => setSelectedChannel(item.channel)}
                      className="accent-[hsl(var(--primary))]"
                    />
                    {item.icon}
                    <div className="flex-1">
                      <p className="font-medium text-sm">{item.label}</p>
                      <p className="text-xs text-[hsl(var(--muted-foreground))]">{item.desc}</p>
                    </div>
                    {selectedChannel === item.channel && <Badge className="text-xs">已选</Badge>}
                  </label>
                ))}
              </CardContent>
            </Card>

            {selectedChannel === 'alipay' && (
              <Card>
                <CardContent className="p-6 space-y-4">
                  <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.25)] p-4">
                    <p className="text-sm font-medium mb-2">支付链接</p>
                    {paymentLink ? (
                      <a
                        href={paymentLink}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sm text-[hsl(var(--primary))] hover:underline break-all"
                      >
                        {paymentLink}
                      </a>
                    ) : (
                      <p className="text-sm text-[hsl(var(--muted-foreground))]">
                        点击下方按钮生成支付宝支付链接
                      </p>
                    )}
                  </div>

                  {paymentLink && (
                    <Button variant="outline" className="w-full" asChild>
                      <a href={paymentLink} target="_blank" rel="noreferrer">
                        <ExternalLink className="h-4 w-4" />
                        打开支付宝支付页
                      </a>
                    </Button>
                  )}

                  {process.env.NODE_ENV !== 'production' && (
                    <Button
                      variant="secondary"
                      className="w-full"
                      onClick={handleDevComplete}
                      disabled={devCompletePayment.isPending}
                    >
                      {devCompletePayment.isPending ? (
                        <>
                          <Loader2 className="h-4 w-4 animate-spin" />
                          模拟支付中...
                        </>
                      ) : (
                        '本地模拟支付成功'
                      )}
                    </Button>
                  )}
                </CardContent>
              </Card>
            )}

            <Button
              className="w-full h-12 text-base"
              onClick={handleCreatePayment}
              disabled={payWithAlipay.isPending || payWithBalance.isPending}
            >
              {payWithAlipay.isPending || payWithBalance.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  支付处理中...
                </>
              ) : (
                `确认支付 ${formatPrice(order.paidAmount)}`
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
