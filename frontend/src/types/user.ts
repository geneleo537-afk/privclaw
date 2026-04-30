export type UserRole = 'user' | 'developer' | 'admin'
export type UserStatus = 'active' | 'suspended' | 'banned'

export interface User {
  id: string
  email: string
  nickname: string
  avatarUrl?: string
  role: UserRole
  status: UserStatus
  bio?: string
  contactInfo?: string
  company?: string
  website?: string
  githubUrl?: string
  emailVerified?: boolean
  isDeveloper?: boolean
  createdAt: string
  lastLoginAt?: string
}
