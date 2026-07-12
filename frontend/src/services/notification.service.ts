import apiClient from '@/services/api-client'
import type { APIResponse, MessageResponse, Notification, NotificationSummary, PaginatedResponse } from '@/types'

export interface NotificationQuery {
  page?: number
  page_size?: number
  unread_only?: boolean
}

export const notificationService = {
  async list(params: NotificationQuery = {}): Promise<PaginatedResponse<Notification>> {
    const { data } = await apiClient.get<PaginatedResponse<Notification>>('/notifications', { params })
    return data
  },

  async unreadCount(): Promise<APIResponse<NotificationSummary>> {
    const { data } = await apiClient.get<APIResponse<NotificationSummary>>('/notifications/unread-count')
    return data
  },

  async markRead(id: string): Promise<APIResponse<Notification>> {
    const { data } = await apiClient.put<APIResponse<Notification>>(`/notifications/${id}/read`)
    return data
  },

  async markAllRead(): Promise<MessageResponse> {
    const { data } = await apiClient.put<MessageResponse>('/notifications/mark-all-read')
    return data
  },

  async remove(id: string): Promise<MessageResponse> {
    const { data } = await apiClient.delete<MessageResponse>(`/notifications/${id}`)
    return data
  },
}
