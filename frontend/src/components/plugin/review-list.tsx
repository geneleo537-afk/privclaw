'use client'

import { useState } from 'react'
import { Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { StarRating } from '@/components/plugin/star-rating'
import { ReviewForm } from '@/components/plugin/review-form'
import { useReviews, useReviewSummary, useDeleteReview } from '@/hooks/use-reviews'
import { useAuthStore } from '@/stores/auth-store'
import { formatDateTime } from '@/lib/utils'

interface ReviewListProps {
  pluginId: string
  hasPurchased: boolean
}

export function ReviewList({ pluginId, hasPurchased }: ReviewListProps) {
  const { isAuthenticated, user } = useAuthStore()
  const summaryQuery = useReviewSummary(pluginId)
  const reviewsQuery = useReviews(pluginId, { page_size: 50 })
  const deleteReview = useDeleteReview(pluginId)
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const summary = summaryQuery.data
  const reviews = reviewsQuery.data?.items ?? []

  const handleDelete = async (reviewId: string) => {
    setDeletingId(reviewId)
    try {
      await deleteReview.mutateAsync(reviewId)
      toast.success('评价已删除')
    } catch (error) {
      const message = error instanceof Error ? error.message : '删除失败'
      toast.error(message)
    } finally {
      setDeletingId(null)
    }
  }

  const hasReviewed = reviews.some((r) => r.userId === user?.id)

  return (
    <Card id="reviews">
      <CardHeader>
        <CardTitle className="text-base">用户评价</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 评分汇总 */}
        {summary && summary.ratingCount > 0 && (
          <div className="flex items-start gap-6">
            <div className="text-center">
              <p className="text-4xl font-bold">{summary.avgRating.toFixed(1)}</p>
              <StarRating value={summary.avgRating} size={18} />
              <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
                {summary.ratingCount} 条评价
              </p>
            </div>
            <div className="flex-1 space-y-1.5">
              {[5, 4, 3, 2, 1].map((star) => {
                const count = summary.ratingDistribution[star] ?? 0
                const pct = summary.ratingCount > 0
                  ? Math.round((count / summary.ratingCount) * 100)
                  : 0
                return (
                  <div key={star} className="flex items-center gap-2 text-sm">
                    <span className="w-3 text-right text-[hsl(var(--muted-foreground))]">
                      {star}
                    </span>
                    <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-amber-400 rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="w-8 text-xs text-[hsl(var(--muted-foreground))]">
                      {count}
                    </span>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {summary && summary.ratingCount === 0 && (
          <p className="text-sm text-[hsl(var(--muted-foreground))]">暂无评价</p>
        )}

        {/* 评价列表 */}
        {reviews.length > 0 && (
          <div className="divide-y divide-[hsl(var(--border))]">
            {reviews.map((review) => (
              <div key={review.id} className="py-4 first:pt-0">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1">
                    <div className="h-8 w-8 shrink-0 rounded-full bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center text-sm font-medium text-orange-700">
                      {review.userNickname.charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-medium">{review.userNickname}</span>
                        <StarRating value={review.rating} size={14} />
                        <span className="text-xs text-[hsl(var(--muted-foreground))]">
                          {formatDateTime(review.createdAt)}
                        </span>
                      </div>
                      {review.title && (
                        <p className="text-sm font-medium mb-0.5">{review.title}</p>
                      )}
                      {review.content && (
                        <p className="text-sm text-[hsl(var(--muted-foreground))] whitespace-pre-line">
                          {review.content}
                        </p>
                      )}
                    </div>
                  </div>
                  {user?.id === review.userId && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-500 hover:text-red-600"
                      disabled={deletingId === review.id}
                      onClick={() => handleDelete(review.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 评价表单或提示 */}
        <div className="pt-4 border-t border-[hsl(var(--border))]">
          {!isAuthenticated ? (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              请先登录后再发表评价
            </p>
          ) : !hasPurchased ? (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              购买该插件后即可发表评价
            </p>
          ) : hasReviewed ? (
            <p className="text-sm text-[hsl(var(--muted-foreground))]">
              你已评价过该插件
            </p>
          ) : (
            <ReviewForm pluginId={pluginId} />
          )}
        </div>
      </CardContent>
    </Card>
  )
}
