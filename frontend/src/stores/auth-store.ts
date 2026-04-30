import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '@/lib/api-client'
import { clearAuthTokens, setAuthTokens } from '@/lib/auth-storage'
import { mapUser, unwrapResponse } from '@/lib/mappers'
import type { ApiResponse } from '@/types/api'
import type { User } from '@/types/user'

interface TokenPayload {
  access_token: string
  refresh_token: string
  expires_in: number
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  hasHydrated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User) => void
  refreshProfile: () => Promise<void>
  setHydrated: (value: boolean) => void
}

async function fetchCurrentUser() {
  const response = await apiClient.get<ApiResponse<Record<string, unknown>>>('/users/me')
  return mapUser(unwrapResponse(response.data))
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      hasHydrated: false,

      login: async (email: string, password: string) => {
        const response = await apiClient.post<ApiResponse<TokenPayload>>('/auth/login', {
          email,
          password,
        })

        const { access_token, refresh_token } = unwrapResponse(response.data)
        setAuthTokens(access_token, refresh_token)
        const user = await fetchCurrentUser()

        set({
          user,
          accessToken: access_token,
          refreshToken: refresh_token,
          isAuthenticated: true,
          hasHydrated: true,
        })
      },

      logout: () => {
        clearAuthTokens()
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          hasHydrated: true,
        })
      },

      setUser: (user: User) => {
        set({ user })
      },

      refreshProfile: async () => {
        const user = await fetchCurrentUser()
        set({ user, isAuthenticated: true, hasHydrated: true })
      },

      setHydrated: (value: boolean) => {
        set({ hasHydrated: value })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        state?.setHydrated(true)
      },
    },
  ),
)
