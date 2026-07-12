import apiClient from '@/services/api-client'
import type { APIResponse, Outlet, OutletPayload, OutletSummary, PaginatedResponse } from '@/types'

export interface OutletQuery {
  page?: number
  page_size?: number
  search?: string
  status?: string
  territory?: string
  business_type?: string
}

export const outletService = {
  async list(params: OutletQuery = {}): Promise<PaginatedResponse<Outlet>> {
    const { data } = await apiClient.get<PaginatedResponse<Outlet>>('/outlets', { params })
    return data
  },

  async summary(): Promise<APIResponse<OutletSummary>> {
    const { data } = await apiClient.get<APIResponse<OutletSummary>>('/outlets/summary')
    return data
  },

  async get(id: string): Promise<APIResponse<Outlet>> {
    const { data } = await apiClient.get<APIResponse<Outlet>>(`/outlets/${id}`)
    return data
  },

  async create(payload: OutletPayload): Promise<APIResponse<Outlet>> {
    const { data } = await apiClient.post<APIResponse<Outlet>>('/outlets', payload)
    return data
  },

  async update(id: string, payload: Partial<OutletPayload>): Promise<APIResponse<Outlet>> {
    const { data } = await apiClient.patch<APIResponse<Outlet>>(`/outlets/${id}`, payload)
    return data
  },

  async remove(id: string): Promise<APIResponse<{ message: string }>> {
    const { data } = await apiClient.delete<APIResponse<{ message: string }>>(`/outlets/${id}`)
    return data
  },

  async addVisit(
    id: string,
    payload: { latitude?: number; longitude?: number; notes?: string; next_follow_up_date?: string },
  ): Promise<APIResponse<Outlet>> {
    const { data } = await apiClient.post<APIResponse<Outlet>>(`/outlets/${id}/visits`, payload)
    return data
  },

  async uploadPhoto(id: string, photoType: string, file: File): Promise<APIResponse<Outlet>> {
    const form = new FormData()
    form.append('file', file)
    const { data } = await apiClient.post<APIResponse<Outlet>>(`/outlets/${id}/photos`, form, {
      params: { photo_type: photoType },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}
