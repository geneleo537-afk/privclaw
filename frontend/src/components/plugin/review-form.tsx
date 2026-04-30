'use client'

import { useState } from 'react'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { StarRating } from '@/components/plugin/star-rating'
import { useCreateReview } from '@/hooks/use-reviews'

interface ReviewFormProps {
  pluginId: string
}

export function ReviewForm({ pluginId }: ReviewFormProps) {
  const [rating, setRating] = useState(0)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const createReview = useCreateReview(pluginId)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (rating === 0) {
      toast.error('请选择评分')
      return
    }
    try {
      await createReview.mutateAsync({ rating, title, content })
      toast.success('评价发表成功')
      setRating(0)
      setTitle('')
      setContent('')
    } catch (error) {
      const message = error instanceof Error ? error.message : '评价发表失败'
      toast.error(message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="text-sm font-medium mb-1.5 block">评分</label>
        <StarRating value={rating} onChange={setRating} size={24} interactive />
      </div>
      <div>
        <label className="text-sm font-medium mb-1.5 block">标题（可选）</label>
        <Input
          placeholder="用一句话概括你的体验"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
        />
      </div>
      <div>
        <label className="text-sm font-medium mb-1.5 block">详细评价（可选）</label>
        <textarea
          className="flex min-h-[100px] w-full rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--background))] px-3 py-2 text-sm placeholder:text-[hsl(var(--muted-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] resize-none"
          placeholder="分享你的使用体验..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          maxLength={5000}
        />
      </div>
      <Button type="submit" disabled={createReview.isPending}>
        {createReview.isPending ? '提交中...' : '发表评价'}
      </Button>
    </form>
  )
}
