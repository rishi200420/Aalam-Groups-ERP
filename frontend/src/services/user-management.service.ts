import apiClient from '@/services/api-client'
import type {
  APIResponse,
  ManagedUser,
  ManagedUserCreatePayload,
  ManagedUserUpdatePayload,
  PaginatedResponse,
} from '@/types'

export interface UserQuery {
  page?: number
  page_size?: number
  search?: string
  role?: string
  is_active?: boolean
}

export const userManagementService = {
  async list(params: UserQuery = {}): Promise<PaginatedResponse<ManagedUser>> {
    const { data } = await apiClient.get<PaginatedResponse<ManagedUser>>('/users', { params })
    return data
  },

  async get(id: string): Promise<APIResponse<ManagedUser>> {
    const { data } = await apiClient.get<APIResponse<ManagedUser>>(`/users/${id}`)
    return data
  },

  async create(payload: ManagedUserCreatePayload): Promise<APIResponse<ManagedUser>> {
    const { data } = await apiClient.post<APIResponse<ManagedUser>>('/users', payload)
    return data
  },

  async update(id: string, payload: ManagedUserUpdatePayload): Promise<APIResponse<ManagedUser>> {
    const { data } = await apiClient.patch<APIResponse<ManagedUser>>(`/users/${id}`, payload)
    return data
  },

  async deactivate(id: string): Promise<APIResponse<ManagedUser>> {
    const { data } = await apiClient.post<APIResponse<ManagedUser>>(`/users/${id}/deactivate`)
    return data
  },

  async activate(id: string): Promise<APIResponse<ManagedUser>> {
    const { data } = await apiClient.post<APIResponse<ManagedUser>>(`/users/${id}/activate`)
    return data
  },

  async resetPassword(id: string, newPassword: string): Promise<APIResponse<{ message: string }>> {
    const { data } = await apiClient.post<APIResponse<{ message: string }>>(`/users/${id}/reset-password`, {
      new_password: newPassword,
    })
    return data
  },

  async remove(id: string): Promise<APIResponse<{ message: string }>> {
    const { data } = await apiClient.delete<APIResponse<{ message: string }>>(`/users/${id}`)
    return data
  },
}
