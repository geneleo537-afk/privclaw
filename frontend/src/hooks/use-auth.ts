'use client'
import { useAuthStore } from '@/stores/auth-store'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

export function useAuth(requireAuth = false) {
  const { user, isAuthenticated, logout } = useAuthStore()
  const router = useRouter()

  useEffect(() => {
    if (requireAuth && !isAuthenticated) {
      router.push('/login')
    }
  }, [requireAuth, isAuthenticated, router])

  return { user, isAuthenticated, logout }
}

export function useRequireAuth() {
  return useAuth(true)
}
