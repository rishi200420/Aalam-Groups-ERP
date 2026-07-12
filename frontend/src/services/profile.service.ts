import apiClient from '@/services/api-client'
import type { APIResponse, ChangePasswordPayload, MessageResponse, Profile, ProfileUpdatePayload } from '@/types'

export const profileService = {
  async get(): Promise<APIResponse<Profile>> {
    const { data } = await apiClient.get<APIResponse<Profile>>('/auth/profile')
    return data
  },

  async update(payload: ProfileUpdatePayload): Promise<APIResponse<Profile>> {
    const { data } = await apiClient.patch<APIResponse<Profile>>('/auth/profile', payload)
    return data
  },

  async changePassword(payload: ChangePasswordPayload): Promise<APIResponse<MessageResponse>> {
    const { data } = await apiClient.post<APIResponse<MessageResponse>>('/auth/profile/change-password', payload)
    return data
  },

  async uploadAvatar(file: File): Promise<APIResponse<Profile>> {
    const formData = new FormData()
    formData.append('file', file)
    const { data } = await apiClient.post<APIResponse<Profile>>('/auth/profile/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}
