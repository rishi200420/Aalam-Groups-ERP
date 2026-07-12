import apiClient from '@/services/api-client'
import type { APIResponse, Dispatch, DispatchCreatePayload, DispatchStatusUpdatePayload } from '@/types'

export interface DispatchQuery {
  search?: string
  status?: string
}

export const dispatchService = {
  async list(params: DispatchQuery = {}): Promise<APIResponse<Dispatch[]>> {
    const { data } = await apiClient.get<APIResponse<Dispatch[]>>('/dispatch', { params })
    return data
  },

  async get(id: string): Promise<APIResponse<Dispatch>> {
    const { data } = await apiClient.get<APIResponse<Dispatch>>(`/dispatch/${id}`)
    return data
  },

  async create(payload: DispatchCreatePayload): Promise<APIResponse<Dispatch>> {
    const { data } = await apiClient.post<APIResponse<Dispatch>>('/dispatch', payload)
    return data
  },

  async update(id: string, payload: DispatchCreatePayload): Promise<APIResponse<Dispatch>> {
    const { data } = await apiClient.put<APIResponse<Dispatch>>(`/dispatch/${id}`, payload)
    return data
  },

  async updateStatus(id: string, payload: DispatchStatusUpdatePayload): Promise<APIResponse<Dispatch>> {
    const { data } = await apiClient.put<APIResponse<Dispatch>>(`/dispatch/${id}/status`, payload)
    return data
  },
}
