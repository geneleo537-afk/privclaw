'use client'

import Image from 'next/image'
import { useState } from 'react'
import { useRouter, useParams } from 'next/navigation'
import { Upload, Plus, X, Loader2, ImageIcon } from 'lucide-react'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

const CATEGORIES = [
  { label: '请选择分类', value: '' },
  { label: '生产力', value: 'productivity' },
  { label: '开发工具', value: 'devtools' },
  { label: 'AI 增强', value: 'ai' },
  { label: '数据分析', value: 'data' },
  { label: '内容创作', value: 'content' },
  { label: '自动化', value: 'automation' },
]

/**
 * Mock 插件数据，实际接入 API 后替换为 usePlugin(id) 的返回值
 */
const MOCK_PLUGIN_DATA: Record<string, {
  name: string
  slug: string
  description: string
  detail: string
  categoryId: string
  price: string
  tags: string[]
  currentVersion: string
}> = {
  '1': {
    name: 'AI 写作助手 Pro',
    slug: 'ai-writer-pro',
    description: '基于大模型的智能写作辅助工具，支持多种写作风格',
    detail: '## 功能介绍\n\n- 智能续写\n- 风格转换\n- 摘要生成\n\n## 使用说明\n\n安装后在编辑器右键菜单中找到 AI 写作助手选项即可使用。',
    categoryId: 'ai',
    price: '49',
    tags: ['AI', '写作', '生产力'],
    currentVersion: '2.3.1',
  },
  '2': {
    name: '代码质量卫士',
    slug: 'code-guardian',
    description: '实时代码质量检测与自动修复工具',
    detail: '## 功能介绍\n\n- 实时 Lint 检测\n- 一键自动修复\n- 质量报告生成',
    categoryId: 'devtools',
    price: '39',
    tags: ['代码质量', '开发工具'],
    currentVersion: '1.5.0',
  },
}

interface PluginEditForm {
  name: string
  slug: string
  description: string
  detail: string
  categoryId: string
  price: string
  tags: string[]
  tagInput: string
}

export default function EditPluginPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const pluginId = params.id

  // 从 Mock 数据中加载，实际 API 接入后替换为 usePlugin(pluginId)
  const existingPlugin = MOCK_PLUGIN_DATA[pluginId]

  const [isLoading, setIsLoading] = useState(false)
  const [coverPreview, setCoverPreview] = useState<string | null>(null)

  const [form, setForm] = useState<PluginEditForm>(() => ({
    name: existingPlugin?.name ?? '',
    slug: existingPlugin?.slug ?? '',
    description: existingPlugin?.description ?? '',
    detail: existingPlugin?.detail ?? '',
    categoryId: existingPlugin?.categoryId ?? '',
    price: existingPlugin?.price ?? '0',
    tags: existingPlugin?.tags ?? [],
    tagInput: '',
  }))

  const updateField = (key: keyof PluginEditForm, value: string) => {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  const addTag = () => {
    const tag = form.tagInput.trim()
    if (tag && !form.tags.includes(tag) && form.tags.length < 6) {
      setForm((prev) => ({ ...prev, tags: [...prev.tags, tag], tagInput: '' }))
    }
  }

  const removeTag = (tag: string) => {
    setForm((prev) => ({ ...prev, tags: prev.tags.filter((t) => t !== tag) }))
  }

  const handleCoverChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > 5 * 1024 * 1024) {
      toast.error('封面图片不能超过 5MB')
      return
    }
    const url = URL.createObjectURL(file)
    setCoverPreview(url)
  }

  const validate = (): string | null => {
    if (!form.name.trim()) return '请填写插件名称'
    if (!form.slug.trim()) return '请填写插件 Slug'
    if (!form.description.trim()) return '请填写插件简介'
    if (!form.categoryId) return '请选择插件分类'
    if (form.description.length < 10) return '简介至少 10 个字符'
    const price = parseFloat(form.price)
    if (isNaN(price) || price < 0) return '价格不合法'
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
    // 模拟保存（接 API 后替换为 apiClient.put(`/plugins/${pluginId}`, ...)）
    await new Promise((resolve) => setTimeout(resolve, 1200))
    toast.success('插件信息已保存')
    router.push('/dashboard/plugins')
    setIsLoading(false)
  }

  if (!existingPlugin) {
    return (
      <div className="max-w-2xl py-12 text-center">
        <p className="text-gray-500">插件不存在或无权编辑</p>
        <Button className="mt-4" variant="outline" onClick={() => router.back()}>
          返回
        </Button>
      </div>
    )
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">编辑插件</h1>
        <p className="text-[hsl(var(--muted-foreground))] text-sm mt-1">
          修改插件信息后保存，部分修改可能需要重新审核
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 基本信息 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">基本信息</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 名称 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">插件名称 *</label>
              <Input
                placeholder="例如：AI 写作助手 Pro"
                value={form.name}
                onChange={(e) => updateField('name', e.target.value)}
                maxLength={50}
                required
              />
            </div>

            {/* Slug */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                插件 Slug *
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">
                  (URL 标识符)
                </span>
              </label>
              <div className="flex">
                <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.5)] text-sm text-[hsl(var(--muted-foreground))]">
                  /plugins/
                </span>
                <Input
                  className="rounded-l-none"
                  placeholder="my-awesome-plugin"
                  value={form.slug}
                  onChange={(e) => updateField('slug', e.target.value)}
                  pattern="[a-z0-9-]+"
                  maxLength={60}
                  required
                />
              </div>
            </div>

            {/* 简介 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                简介 *
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">
                  ({form.description.length}/200)
                </span>
              </label>
              <textarea
                className="flex min-h-20 w-full rounded-md border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-3 py-2 text-sm ring-offset-background placeholder:text-[hsl(var(--muted-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                placeholder="用一两句话描述插件的核心功能..."
                value={form.description}
                onChange={(e) => updateField('description', e.target.value)}
                maxLength={200}
                required
                rows={3}
              />
            </div>

            {/* 详细说明 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                详细说明
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">
                  (支持 Markdown)
                </span>
              </label>
              <textarea
                className="flex min-h-40 w-full rounded-md border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-3 py-2 text-sm ring-offset-background placeholder:text-[hsl(var(--muted-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none font-mono"
                placeholder="## 功能介绍&#10;&#10;详细描述插件的功能、使用方法、注意事项..."
                value={form.detail}
                onChange={(e) => updateField('detail', e.target.value)}
                rows={8}
              />
            </div>
          </CardContent>
        </Card>

        {/* 分类 + 标签 + 价格 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">分类与定价</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 分类 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">分类 *</label>
              <select
                className="flex h-10 w-full rounded-md border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
                value={form.categoryId}
                onChange={(e) => updateField('categoryId', e.target.value)}
                required
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat.value} value={cat.value} disabled={!cat.value}>
                    {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* 标签 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">
                标签
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">
                  (最多 6 个)
                </span>
              </label>
              <div className="flex gap-2">
                <Input
                  placeholder="添加标签后按 Enter"
                  value={form.tagInput}
                  onChange={(e) => updateField('tagInput', e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      addTag()
                    }
                  }}
                  maxLength={20}
                />
                <Button type="button" variant="outline" size="sm" onClick={addTag}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              {form.tags.length > 0 && (
                <div className="flex flex-wrap gap-1.5">
                  {form.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 rounded-full bg-[hsl(var(--secondary))] px-2.5 py-0.5 text-xs font-medium"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => removeTag(tag)}
                        className="hover:text-red-500"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* 价格 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">价格（元）</label>
              <div className="flex">
                <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.5)] text-sm text-[hsl(var(--muted-foreground))]">
                  ¥
                </span>
                <Input
                  type="number"
                  className="rounded-l-none"
                  placeholder="0 = 免费"
                  value={form.price}
                  onChange={(e) => updateField('price', e.target.value)}
                  min="0"
                  max="9999"
                  step="1"
                />
              </div>
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                修改价格将对新购买者生效，已购买用户不受影响
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 封面图更新 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">封面图片</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-start gap-4">
              <div className="h-24 w-40 rounded-xl border-2 border-dashed border-[hsl(var(--border))] bg-[hsl(var(--muted)/0.3)] flex items-center justify-center overflow-hidden shrink-0">
                {coverPreview ? (
                  <Image
                    src={coverPreview}
                    alt="封面预览"
                    width={160}
                    height={96}
                    className="h-full w-full object-cover"
                    unoptimized
                  />
                ) : (
                  <div className="text-center">
                    <ImageIcon className="h-6 w-6 mx-auto text-[hsl(var(--muted-foreground)/0.5)]" />
                    <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">当前封面</p>
                  </div>
                )}
              </div>
              <div>
                <label className="cursor-pointer">
                  <Button type="button" variant="outline" size="sm" asChild>
                    <span>
                      <Upload className="h-3.5 w-3.5" />
                      更换封面
                    </span>
                  </Button>
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    className="hidden"
                    onChange={handleCoverChange}
                  />
                </label>
                <p className="text-xs text-[hsl(var(--muted-foreground))] mt-2 leading-relaxed">
                  支持 JPG、PNG、WebP
                  <br />
                  建议尺寸 1280×720，不超过 5MB
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 提交 */}
        <div className="flex gap-3">
          <Button type="submit" disabled={isLoading} className="flex-1 sm:flex-none sm:px-10">
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                保存中...
              </>
            ) : (
              '保存修改'
            )}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => router.back()}
            disabled={isLoading}
          >
            取消
          </Button>
        </div>
      </form>
    </div>
  )
}
