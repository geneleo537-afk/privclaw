export type OrderStatus = 'pending' | 'paid' | 'closed' | 'cancelled' | 'refunded'
export type PayChannel = 'alipay' | 'wechat' | 'balance'

export interface Order {
  id: string
  orderNo: string
  pluginSnapshot: {
    id?: string
    name: string
    price: number
    iconUrl?: string
    summary?: string
    version?: string
  }
  paidAmount: number
  platformFee: number
  developerRevenue: number
  payChannel?: PayChannel
  status: OrderStatus
  paidAt?: string
  expiresAt?: string
  createdAt: string
}

export interface OrderStatusSnapshot {
  orderId: string
  orderNo: string
  status: OrderStatus
  paidAt?: string
  expiresAt?: string
}

export interface PaymentSession {
  orderId: string
  orderNo: string
  amount: number
  qrCodeUrl: string
}
