'use client'

import Image from 'next/image'
import { useState } from 'react'
import { Loader2, Camera, User, Lock, Link as LinkIcon } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuthStore } from '@/stores/auth-store'

export default function SettingsPage() {
  const { user, setUser } = useAuthStore()

  const [profileForm, setProfileForm] = useState({
    nickname: user?.nickname ?? '',
    bio: user?.bio ?? '',
  })
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [contactForm, setContactForm] = useState({
    contactInfo: user?.contactInfo ?? '',
  })

  const [savingProfile, setSavingProfile] = useState(false)
  const [savingPassword, setSavingPassword] = useState(false)
  const [savingContact, setSavingContact] = useState(false)

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!profileForm.nickname.trim()) {
      toast.error('昵称不能为空')
      return
    }
    setSavingProfile(true)
    await new Promise((r) => setTimeout(r, 1000))
    if (user) {
      setUser({ ...user, nickname: profileForm.nickname.trim(), bio: profileForm.bio.trim() })
    }
    toast.success('个人资料已更新')
    setSavingProfile(false)
  }

  const handleSavePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!passwordForm.currentPassword) {
      toast.error('请输入当前密码')
      return
    }
    if (passwordForm.newPassword.length < 8) {
      toast.error('新密码至少 8 位')
      return
    }
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error('两次输入的新密码不一致')
      return
    }
    setSavingPassword(true)
    await new Promise((r) => setTimeout(r, 1000))
    toast.success('密码已修改')
    setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
    setSavingPassword(false)
  }

  const handleSaveContact = async (e: React.FormEvent) => {
    e.preventDefault()
    setSavingContact(true)
    await new Promise((r) => setTimeout(r, 800))
    if (user) {
      setUser({ ...user, contactInfo: contactForm.contactInfo.trim() })
    }
    toast.success('联系方式已更新')
    setSavingContact(false)
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">账户设置</h1>
        <p className="text-[hsl(var(--muted-foreground))] text-sm mt-1">管理你的个人资料和安全设置</p>
      </div>

      {/* 头像区 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <User className="h-4 w-4" />
            头像
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-5">
            <div className="relative">
              <div className="h-16 w-16 rounded-full bg-[hsl(var(--primary)/0.15)] flex items-center justify-center text-[hsl(var(--primary))] text-2xl font-bold overflow-hidden">
                {user?.avatarUrl ? (
                  <Image
                    src={user.avatarUrl}
                    alt="头像"
                    width={64}
                    height={64}
                    className="h-full w-full object-cover"
                    unoptimized
                  />
                ) : (
                  user?.nickname?.charAt(0)?.toUpperCase() ?? '?'
                )}
              </div>
              <label className="absolute -bottom-1 -right-1 cursor-pointer">
                <div className="h-6 w-6 rounded-full bg-[hsl(var(--primary))] flex items-center justify-center hover:bg-[hsl(15,75%,48%)] transition-colors shadow-sm">
                  <Camera className="h-3 w-3 text-white" />
                </div>
                <input type="file" accept="image/*" className="hidden" />
              </label>
            </div>
            <div>
              <p className="text-sm font-medium">{user?.nickname}</p>
              <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{user?.email}</p>
              <p className="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">
                点击头像旁的相机图标更换头像（PNG/JPG，最大 2MB）
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 基本信息 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <User className="h-4 w-4" />
            基本信息
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSaveProfile} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">昵称</label>
              <Input
                value={profileForm.nickname}
                onChange={(e) => setProfileForm((prev) => ({ ...prev, nickname: e.target.value }))}
                placeholder="你的昵称"
                maxLength={20}
                disabled={savingProfile}
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium">个人简介</label>
              <textarea
                className="flex min-h-24 w-full rounded-md border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-3 py-2 text-sm ring-offset-background placeholder:text-[hsl(var(--muted-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                placeholder="简单介绍一下你自己..."
                value={profileForm.bio}
                onChange={(e) => setProfileForm((prev) => ({ ...prev, bio: e.target.value }))}
                maxLength={200}
                disabled={savingProfile}
                rows={3}
              />
            </div>

            <Button type="submit" disabled={savingProfile}>
              {savingProfile ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  保存中...
                </>
              ) : (
                '保存修改'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* 修改密码 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Lock className="h-4 w-4" />
            修改密码
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSavePassword} className="space-y-4">
            {[
              { key: 'currentPassword', label: '当前密码', placeholder: '输入当前密码' },
              { key: 'newPassword', label: '新密码', placeholder: '至少 8 位' },
              { key: 'confirmPassword', label: '确认新密码', placeholder: '再次输入新密码' },
            ].map((field) => (
              <div key={field.key} className="space-y-1.5">
                <label className="text-sm font-medium">{field.label}</label>
                <Input
                  type="password"
                  placeholder={field.placeholder}
                  value={passwordForm[field.key as keyof typeof passwordForm]}
                  onChange={(e) =>
                    setPasswordForm((prev) => ({ ...prev, [field.key]: e.target.value }))
                  }
                  disabled={savingPassword}
                />
              </div>
            ))}

            <Button type="submit" variant="outline" disabled={savingPassword}>
              {savingPassword ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  修改中...
                </>
              ) : (
                '修改密码'
              )}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* 开发者联系方式 */}
      {(user?.role === 'developer' || user?.role === 'admin') && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <LinkIcon className="h-4 w-4" />
              开发者联系方式
            </CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSaveContact} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-sm font-medium">联系方式</label>
                <textarea
                  className="flex min-h-24 w-full rounded-md border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-3 py-2 text-sm ring-offset-background placeholder:text-[hsl(var(--muted-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                  placeholder="邮箱、微信、GitHub 主页等联系方式，将显示在你的插件详情页"
                  value={contactForm.contactInfo}
                  onChange={(e) => setContactForm({ contactInfo: e.target.value })}
                  maxLength={500}
                  disabled={savingContact}
                  rows={3}
                />
              </div>

              <Button type="submit" variant="outline" disabled={savingContact}>
                {savingContact ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    保存中...
                  </>
                ) : (
                  '保存联系方式'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
