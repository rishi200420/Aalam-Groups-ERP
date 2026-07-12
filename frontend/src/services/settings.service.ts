import apiClient from '@/services/api-client'
import type {
  APIResponse,
  NotificationPreference,
  NotificationPreferenceUpdatePayload,
  SystemSettings,
  SystemSettingsUpdatePayload,
} from '@/types'

export const settingsService = {
  async getSystemSettings(): Promise<APIResponse<SystemSettings>> {
    const { data } = await apiClient.get<APIResponse<SystemSettings>>('/settings/system')
    return data
  },

  async updateSystemSettings(payload: SystemSettingsUpdatePayload): Promise<APIResponse<SystemSettings>> {
    const { data } = await apiClient.put<APIResponse<SystemSettings>>('/settings/system', payload)
    return data
  },

  async getNotificationPreferences(): Promise<APIResponse<NotificationPreference>> {
    const { data } = await apiClient.get<APIResponse<NotificationPreference>>('/settings/notification-preferences')
    return data
  },

  async updateNotificationPreferences(payload: NotificationPreferenceUpdatePayload): Promise<APIResponse<NotificationPreference>> {
    const { data } = await apiClient.put<APIResponse<NotificationPreference>>('/settings/notification-preferences', payload)
    return data
  },
}
