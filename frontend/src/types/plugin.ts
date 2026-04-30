export type PluginStatus = string

export interface PluginListItem {
  id: string
  name: string
  slug: string
  summary: string
  iconUrl?: string
  price: number
  isFree: boolean
  status: PluginStatus | string
  currentVersion?: string
  downloadCount: number
  avgRating: number
  ratingCount: number
  developerId: string
  developerName: string
  categoryName?: string
  categorySlug?: string
}

export interface Plugin {
  id: string
  name: string
  slug: string
  summary: string
  description: string
  iconUrl?: string
  screenshots: string[]
  price: number
  currency: string
  isFree: boolean
  status: PluginStatus | string
  reviewStatus: string
  currentVersion?: string
  currentVersionId?: string
  downloadCount: number
  purchaseCount: number
  avgRating: number
  ratingCount: number
  developerId: string
  developerName: string
  categoryId?: string
  categoryName?: string
  categorySlug?: string
  tags: string[]
  publishedAt?: string
  createdAt: string
  updatedAt: string
}

export interface PluginVersion {
  id: string
  version: string
  changelog?: string
  fileSize: number
  downloadCount: number
  publishedAt?: string
  createdAt: string
}
