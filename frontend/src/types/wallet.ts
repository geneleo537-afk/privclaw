export interface WalletOverview {
  balance: number
  totalEarned: number
  totalWithdrawn: number
}

export interface WalletTransaction {
  id: string
  type: string
  direction: string
  amount: number
  balanceAfter: number
  description: string
  createdAt: string
}

export interface PurchaseItem {
  purchaseId: string
  pluginId: string
  pluginName: string
  pluginSlug: string
  pluginIconUrl?: string
  pluginVersion?: string
  purchasedAt: string
}

export interface WithdrawalItem {
  id: string
  settlementNo: string
  amount: number
  alipayAccount: string
  status: string
  requestedAt: string
  completedAt?: string
  failureReason?: string
}
