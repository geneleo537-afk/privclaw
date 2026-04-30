export interface Review {
  id: string
  pluginId: string
  userId: string
  orderId?: string
  rating: number
  title: string
  content: string
  isVisible: boolean
  createdAt: string
  updatedAt: string
  userNickname: string
  userAvatarUrl: string
}

export interface ReviewSummary {
  avgRating: number
  ratingCount: number
  ratingDistribution: Record<number, number>
}

export interface CreateReviewPayload {
  rating: number
  title: string
  content: string
}
