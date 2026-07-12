import axios from 'axios'
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { authService } from '@/services/auth.service'
import type { User, UserRole } from '@/types'
import { isDistributorRole, isFounderRole } from '@/types'

interface AuthContextValue {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string, rememberSession?: boolean) => Promise<User>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
  primaryRole: UserRole | null
  isFounder: boolean
  isDistributor: boolean
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => authService.getStoredUser())
  const [isLoading, setIsLoading] = useState(true)

  const hydrateSession = useCallback(async () => {
    if (!authService.isAuthenticated()) {
      setUser(null)
      setIsLoading(false)
      return
    }

    try {
      const response = await authService.getMe()
      if (response.success && response.data) {
        setUser(response.data)
        authService.persistUser(response.data)
      } else {
        authService.clearSession()
        setUser(null)
      }
    } catch {
      authService.clearSession()
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    void hydrateSession()
  }, [hydrateSession])

  const login = useCallback(async (email: string, password: string, rememberSession = true) => {
    try {
      const response = await authService.login({ email, password })
      if (!response.success || !response.data) {
        throw new Error(response.message || 'Login failed')
      }
      authService.setSession(response.data, rememberSession)
      setUser(response.data.user)
      return response.data.user
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const message = (error.response?.data as { message?: string } | undefined)?.message
        throw new Error(message || 'Invalid email or password')
      }
      throw error
    }
  }, [])

  const logout = useCallback(async () => {
    await authService.logout()
    setUser(null)
  }, [])

  const refreshUser = useCallback(async () => {
    const response = await authService.getMe()
    if (response.success && response.data) {
      setUser(response.data)
      authService.persistUser(response.data)
    }
  }, [])

  const primaryRole = user?.primary_role ?? user?.roles?.[0] ?? null

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user && authService.isAuthenticated(),
      isLoading,
      login,
      logout,
      refreshUser,
      primaryRole,
      isFounder: isFounderRole(primaryRole),
      isDistributor: isDistributorRole(primaryRole),
    }),
    [user, isLoading, login, logout, refreshUser, primaryRole],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}
