'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Loader2, Check } from 'lucide-react'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import apiClient from '@/lib/api-client'
import { useAuthStore } from '@/stores/auth-store'

export default function RegisterPage() {
  const router = useRouter()
  const { login } = useAuthStore()

  const [form, setForm] = useState({
    nickname: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeTerms: false,
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleChange = (key: keyof typeof form) => (
    e: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const validate = (): string | null => {
    if (!form.nickname.trim()) return '请输入昵称'
    if (form.nickname.length < 2) return '昵称至少 2 个字符'
    if (!form.email.trim()) return '请输入邮箱'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) return '邮箱格式不正确'
    if (form.password.length < 8) return '密码至少 8 位'
    if (!/[A-Za-z]/.test(form.password)) return '密码必须包含字母'
    if (!/\d/.test(form.password)) return '密码必须包含数字'
    if (form.password !== form.confirmPassword) return '两次输入的密码不一致'
    if (!form.agreeTerms) return '请同意使用条款'
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const error = validate()
    if (error) {
      toast.error(error)
      return
    }

    setIsLoading(true)
    try {
      await apiClient.post('/auth/register', {
        nickname: form.nickname.trim(),
        email: form.email.trim(),
        password: form.password,
      })
      await login(form.email.trim(), form.password)
      toast.success('注册成功，已自动登录')
      router.push('/dashboard')
    } catch (err) {
      const message = err instanceof Error ? err.message : '注册失败，请稍后重试'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  const passwordStrength = (() => {
    const p = form.password
    if (!p) return 0
    let score = 0
    if (p.length >= 8) score++
    if (/[A-Z]/.test(p)) score++
    if (/[0-9]/.test(p)) score++
    if (/[^A-Za-z0-9]/.test(p)) score++
    return score
  })()

  const strengthLabels = ['', '弱', '一般', '较强', '强']
  const strengthColors = ['', 'bg-red-400', 'bg-amber-400', 'bg-blue-400', 'bg-green-400']

  return (
    <Card className="border-[hsl(var(--border))] shadow-md">
      <CardHeader className="space-y-1 pb-4">
        <CardTitle className="text-2xl font-bold">创建账户</CardTitle>
        <CardDescription>注册 PrivClaw，开启 AI 定制服务之旅</CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 昵称 */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium" htmlFor="nickname">昵称</label>
            <Input
              id="nickname"
              placeholder="你的昵称（2-20 个字符）"
              value={form.nickname}
              onChange={handleChange('nickname')}
              maxLength={20}
              disabled={isLoading}
              required
            />
          </div>

          {/* 邮箱 */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium" htmlFor="reg-email">邮箱地址</label>
            <Input
              id="reg-email"
              type="email"
              placeholder="your@email.com"
              value={form.email}
              onChange={handleChange('email')}
              autoComplete="email"
              disabled={isLoading}
              required
            />
          </div>

          {/* 密码 */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium" htmlFor="reg-password">密码</label>
            <div className="relative">
              <Input
                id="reg-password"
                type={showPassword ? 'text' : 'password'}
                placeholder="至少 8 位"
                value={form.password}
                onChange={handleChange('password')}
                autoComplete="new-password"
                disabled={isLoading}
                required
                className="pr-10"
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
                onClick={() => setShowPassword(!showPassword)}
                tabIndex={-1}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {/* 密码强度条 */}
            {form.password && (
              <div className="flex items-center gap-2 mt-1">
                <div className="flex gap-1 flex-1">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className={`h-1 flex-1 rounded-full transition-all ${
                        i <= passwordStrength ? strengthColors[passwordStrength] : 'bg-[hsl(var(--border))]'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-xs text-[hsl(var(--muted-foreground))]">
                  {strengthLabels[passwordStrength]}
                </span>
              </div>
            )}
          </div>

          {/* 确认密码 */}
          <div className="space-y-1.5">
            <label className="text-sm font-medium" htmlFor="confirm-password">确认密码</label>
            <div className="relative">
              <Input
                id="confirm-password"
                type={showConfirm ? 'text' : 'password'}
                placeholder="再次输入密码"
                value={form.confirmPassword}
                onChange={handleChange('confirmPassword')}
                autoComplete="new-password"
                disabled={isLoading}
                required
                className="pr-10"
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
                onClick={() => setShowConfirm(!showConfirm)}
                tabIndex={-1}
              >
                {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            {/* 密码一致性提示 */}
            {form.confirmPassword && (
              <p className={`text-xs flex items-center gap-1 ${
                form.password === form.confirmPassword ? 'text-green-600' : 'text-red-500'
              }`}>
                <Check className="h-3 w-3" />
                {form.password === form.confirmPassword ? '密码一致' : '密码不一致'}
              </p>
            )}
          </div>

          {/* 同意条款 */}
          <div className="flex items-start gap-2.5">
            <input
              type="checkbox"
              id="agree-terms"
              checked={form.agreeTerms}
              onChange={handleChange('agreeTerms')}
              disabled={isLoading}
              className="mt-0.5 h-4 w-4 rounded border-[hsl(var(--border))] accent-[hsl(var(--primary))]"
            />
            <label htmlFor="agree-terms" className="text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">
              我已阅读并同意{' '}
              <Link href="/terms" className="text-[hsl(var(--primary))] hover:underline">
                使用条款
              </Link>{' '}
              和{' '}
              <Link href="/privacy" className="text-[hsl(var(--primary))] hover:underline">
                隐私政策
              </Link>
            </label>
          </div>

          {/* 注册按钮 */}
          <Button
            type="submit"
            className="w-full h-11"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                注册中...
              </>
            ) : (
              '创建账户'
            )}
          </Button>
        </form>

        {/* 登录链接 */}
        <div className="mt-6 text-center text-sm text-[hsl(var(--muted-foreground))]">
          已有账户？{' '}
          <Link href="/login" className="font-medium text-[hsl(var(--primary))] hover:underline">
            立即登录
          </Link>
        </div>
      </CardContent>
    </Card>
  )
}
