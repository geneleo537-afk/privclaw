'use client'

import Image from 'next/image'
import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, Plus, X, Loader2, ImageIcon, FileArchive } from 'lucide-react'
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

interface PluginForm {
  name: string
  slug: string
  description: string
  detail: string
  categoryId: string
  price: string
  version: string
  tags: string[]
  tagInput: string
}

export default function NewPluginPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [coverPreview, setCoverPreview] = useState<string | null>(null)
  const [pluginFile, setPluginFile] = useState<File | null>(null)

  const [form, setForm] = useState<PluginForm>({
    name: '',
    slug: '',
    description: '',
    detail: '',
    categoryId: '',
    price: '0',
    version: '1.0.0',
    tags: [],
    tagInput: '',
  })

  const updateField = (key: keyof PluginForm, value: string) => {
    setForm((prev) => {
      const next: PluginForm = { ...prev, [key]: value }
      // 自动生成 slug
      if (key === 'name') {
        next.slug = value
          .toLowerCase()
          .replace(/[\s\W]+/g, '-')
          .replace(/^-+|-+$/g, '')
      }
      return next
    })
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

  const handlePluginFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (file.size > 100 * 1024 * 1024) {
      toast.error('插件文件不能超过 100MB')
      return
    }
    setPluginFile(file)
  }

  const validate = (): string | null => {
    if (!form.name.trim()) return '请填写插件名称'
    if (!form.slug.trim()) return '请填写插件 Slug'
    if (!form.description.trim()) return '请填写插件简介'
    if (!form.categoryId) return '请选择插件分类'
    if (form.description.length < 10) return '简介至少 10 个字符'
    const price = parseFloat(form.price)
    if (isNaN(price) || price < 0) return '价格不合法'
    if (!pluginFile) return '请上传插件文件（.zip）'
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
    // 模拟提交（实际接 API 时替换）
    await new Promise((resolve) => setTimeout(resolve, 1500))
    toast.success('插件发布成功！正在等待审核...')
    router.push('/dashboard/plugins')
    setIsLoading(false)
  }

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">发布能力模块</h1>
        <p className="text-[hsl(var(--muted-foreground))] text-sm mt-1">
          填写能力模块信息后提交审核，审核通过后将上架
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
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">(URL 标识符)</span>
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
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">({form.description.length}/200)</span>
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
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">(支持 Markdown)</span>
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
                <span className="font-normal text-[hsl(var(--muted-foreground))] ml-1">(最多 6 个)</span>
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
                      <button type="button" onClick={() => removeTag(tag)} className="hover:text-red-500">
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
                填写 0 表示免费，付费插件需遵守平台定价规范（最低 ¥1）
              </p>
            </div>

            {/* 版本号 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">初始版本号</label>
              <Input
                placeholder="例如：1.0.0"
                value={form.version}
                onChange={(e) => updateField('version', e.target.value)}
                pattern="\d+\.\d+\.\d+"
              />
            </div>
          </CardContent>
        </Card>

        {/* 文件上传 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">文件上传</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 封面图 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">封面图片</label>
              <div className="flex items-start gap-4">
                {/* 预览区 */}
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
                      <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">16:9</p>
                    </div>
                  )}
                </div>
                <div>
                  <label className="cursor-pointer">
                    <Button type="button" variant="outline" size="sm" asChild>
                      <span>
                        <Upload className="h-3.5 w-3.5" />
                        选择图片
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
                    支持 JPG、PNG、WebP<br />
                    建议尺寸 1280×720，不超过 5MB
                  </p>
                </div>
              </div>
            </div>

            {/* 插件文件 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium">插件文件 * <span className="font-normal text-[hsl(var(--muted-foreground))]">(.zip)</span></label>
              <label className="cursor-pointer">
                <div className={`flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition-colors ${
                  pluginFile
                    ? 'border-[hsl(var(--primary)/0.4)] bg-[hsl(var(--primary)/0.05)]'
                    : 'border-[hsl(var(--border))] hover:border-[hsl(var(--primary)/0.3)] hover:bg-[hsl(var(--muted)/0.3)]'
                }`}>
                  {pluginFile ? (
                    <>
                      <FileArchive className="h-8 w-8 text-[hsl(var(--primary))] mb-2" />
                      <p className="text-sm font-medium">{pluginFile.name}</p>
                      <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
                        {(pluginFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </>
                  ) : (
                    <>
                      <Upload className="h-8 w-8 text-[hsl(var(--muted-foreground)/0.4)] mb-2" />
                      <p className="text-sm font-medium text-[hsl(var(--muted-foreground))]">点击或拖放文件到此处</p>
                      <p className="text-xs text-[hsl(var(--muted-foreground)/0.6)] mt-1">仅支持 .zip 格式，最大 100MB</p>
                    </>
                  )}
                </div>
                <input
                  type="file"
                  accept=".zip"
                  className="hidden"
                  onChange={handlePluginFileChange}
                />
              </label>
            </div>
          </CardContent>
        </Card>

        {/* 提交 */}
        <div className="flex gap-3">
          <Button type="submit" disabled={isLoading} className="flex-1 sm:flex-none sm:px-10">
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                提交审核中...
              </>
            ) : (
              '提交审核'
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
