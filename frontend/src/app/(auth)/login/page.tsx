'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, ArrowRight, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/stores/auth-store'

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuthStore()

  const [email, setEmail]             = useState('')
  const [password, setPassword]       = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading]     = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim() || !password.trim()) {
      toast.error('请填写邮箱和密码')
      return
    }
    setIsLoading(true)
    try {
      await login(email.trim(), password)
      toast.success('登录成功，欢迎回来！')
      router.push('/dashboard')
    } catch (err) {
      const message = err instanceof Error ? err.message : '登录失败，请检查邮箱和密码'
      toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      {/* 页头文字 */}
      <h1 className="text-3xl font-black text-gray-900 mb-2">
        欢迎回来
      </h1>
      <p className="text-sm text-gray-400 mb-10">
        还没有账号？{' '}
        <Link
          href="/register"
          className="font-bold hover:opacity-70 transition-opacity"
          style={{ color: '#EB4C4C' }}
        >
          免费注册
        </Link>
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 邮箱 */}
        <div>
          <label className="block text-xs font-bold uppercase tracking-widest text-gray-400 mb-2"
            htmlFor="email">
            邮箱地址
          </label>
          <Input
            id="email"
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            required
            disabled={isLoading}
            className="h-12 rounded-xl border-2 border-gray-200 focus-visible:ring-0 text-base"
            style={{ transition: 'border-color 0.2s' }}
            onFocus={e => (e.currentTarget.style.borderColor = '#EB4C4C')}
            onBlur={e => (e.currentTarget.style.borderColor = '')}
          />
        </div>

        {/* 密码 */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-xs font-bold uppercase tracking-widest text-gray-400"
              htmlFor="password">
              密码
            </label>
            <Link
              href="/forgot-password"
              className="text-xs text-gray-400 hover:text-[#EB4C4C] transition-colors"
            >
              忘记密码？
            </Link>
          </div>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="输入你的密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              disabled={isLoading}
              className="h-12 rounded-xl border-2 border-gray-200 focus-visible:ring-0 text-base pr-12"
              onFocus={e => (e.currentTarget.style.borderColor = '#EB4C4C')}
              onBlur={e => (e.currentTarget.style.borderColor = '')}
            />
            <button
              type="button"
              className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              onClick={() => setShowPassword(!showPassword)}
              tabIndex={-1}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </div>

        {/* 登录按钮 */}
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full h-12 rounded-xl text-base font-bold border-0 hover:opacity-90 transition-opacity"
          style={{ backgroundColor: '#EB4C4C', color: 'white' }}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              登录中...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              登录账号
              <ArrowRight className="h-4 w-4" />
            </span>
          )}
        </Button>
      </form>

      {/* 条款 */}
      <p className="mt-8 text-center text-xs text-gray-400">
        登录即代表你同意我们的{' '}
        <Link href="/terms" className="underline hover:text-gray-600 transition-colors">服务条款</Link>
        {' '}和{' '}
        <Link href="/privacy" className="underline hover:text-gray-600 transition-colors">隐私政策</Link>
      </p>
    </div>
  )
}
