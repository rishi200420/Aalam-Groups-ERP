import apiClient from '@/services/api-client'
import type { APIResponse, LoginResponse, User } from '@/types'

const TOKEN_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'
const USER_KEY = 'auth_user'
const SESSION_SCOPE_KEY = 'auth_storage_scope'

type AuthStorageScope = 'local' | 'session'

function getAuthStorage(): Storage {
  return localStorage.getItem(SESSION_SCOPE_KEY) === 'session' ? sessionStorage : localStorage
}

function readStoredValue(key: string): string | null {
  return sessionStorage.getItem(key) ?? localStorage.getItem(key)
}

function removeStoredValue(key: string): void {
  localStorage.removeItem(key)
  sessionStorage.removeItem(key)
}

export const authService = {
  async login(credentials: { email: string; password: string }): Promise<APIResponse<LoginResponse>> {
    const { data } = await apiClient.post<APIResponse<LoginResponse>>('/auth/login', credentials)
    return data
  },

  async refresh(refreshToken: string): Promise<APIResponse<LoginResponse>> {
    const { data } = await apiClient.post<APIResponse<LoginResponse>>('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return data
  },

  async logout(): Promise<void> {
    const refreshToken = localStorage.getItem(REFRESH_KEY) ?? sessionStorage.getItem(REFRESH_KEY)
    try {
      if (refreshToken) {
        await apiClient.post('/auth/logout', { refresh_token: refreshToken })
      }
    } catch {
      // Ignore backend/network failures on logout — the session must still be cleared locally.
    } finally {
      this.clearSession()
    }
  },

  async getMe(): Promise<APIResponse<User>> {
    const { data } = await apiClient.get<APIResponse<User>>('/auth/me')
    return data
  },

  async forgotPassword(email: string): Promise<APIResponse<{ message: string }>> {
    const { data } = await apiClient.post<APIResponse<{ message: string }>>('/auth/forgot-password', {
      email,
    })
    return data
  },

  setSession(loginData: LoginResponse, rememberSession = true): void {
    const scope: AuthStorageScope = rememberSession ? 'local' : 'session'
    const storage = scope === 'local' ? localStorage : sessionStorage

    removeStoredValue(TOKEN_KEY)
    removeStoredValue(REFRESH_KEY)
    removeStoredValue(USER_KEY)

    localStorage.setItem(SESSION_SCOPE_KEY, scope)
    storage.setItem(TOKEN_KEY, loginData.access_token)
    storage.setItem(REFRESH_KEY, loginData.refresh_token)
    storage.setItem(USER_KEY, JSON.stringify(loginData.user))
  },

  updateSession(loginData: LoginResponse): void {
    const rememberSession = localStorage.getItem(SESSION_SCOPE_KEY) !== 'session'
    this.setSession(loginData, rememberSession)
  },

  persistUser(user: User): void {
    getAuthStorage().setItem(USER_KEY, JSON.stringify(user))
  },

  clearSession(): void {
    removeStoredValue(TOKEN_KEY)
    removeStoredValue(REFRESH_KEY)
    removeStoredValue(USER_KEY)
    localStorage.removeItem(SESSION_SCOPE_KEY)
  },

  getAccessToken(): string | null {
    return readStoredValue(TOKEN_KEY)
  },

  getRefreshToken(): string | null {
    return readStoredValue(REFRESH_KEY)
  },

  getStoredUser(): User | null {
    const raw = getAuthStorage().getItem(USER_KEY) ?? readStoredValue(USER_KEY)
    if (!raw) return null
    try {
      return JSON.parse(raw) as User
    } catch {
      return null
    }
  },

  isAuthenticated(): boolean {
    return !!readStoredValue(TOKEN_KEY)
  },
}
