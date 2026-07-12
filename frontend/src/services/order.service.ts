import apiClient from '@/services/api-client'
import type { APIResponse, Order, OrderCreatePayload, OrderSummary, PaginatedResponse } from '@/types'

export interface OrderQuery {
  page?: number
  page_size?: number
  search?: string
  status?: string
  outlet_id?: string
  distributor_id?: string
}

export const orderService = {
  async list(params: OrderQuery = {}): Promise<PaginatedResponse<Order>> {
    const { data } = await apiClient.get<PaginatedResponse<Order>>('/orders', { params })
    return data
  },

  async summary(): Promise<APIResponse<OrderSummary>> {
    const { data } = await apiClient.get<APIResponse<OrderSummary>>('/orders/summary')
    return data
  },

  async get(id: string): Promise<APIResponse<Order>> {
    const { data } = await apiClient.get<APIResponse<Order>>(`/orders/${id}`)
    return data
  },

  async create(payload: OrderCreatePayload): Promise<APIResponse<Order>> {
    const { data } = await apiClient.post<APIResponse<Order>>('/orders', payload)
    return data
  },

  async approve(id: string): Promise<APIResponse<Order>> {
    const { data } = await apiClient.post<APIResponse<Order>>(`/orders/${id}/approve`)
    return data
  },

  async reject(id: string, reason: string): Promise<APIResponse<Order>> {
    const { data } = await apiClient.post<APIResponse<Order>>(`/orders/${id}/reject`, null, { params: { reason } })
    return data
  },

  async cancel(id: string, reason: string): Promise<APIResponse<Order>> {
    const { data } = await apiClient.post<APIResponse<Order>>(`/orders/${id}/cancel`, null, { params: { reason } })
    return data
  },

  async advanceStatus(id: string, status: string): Promise<APIResponse<Order>> {
    const { data } = await apiClient.post<APIResponse<Order>>(`/orders/${id}/status`, { status })
    return data
  },

  async assignDistributor(id: string, distributorId: string): Promise<APIResponse<Order>> {
    const { data } = await apiClient.post<APIResponse<Order>>(`/orders/${id}/assign-distributor`, null, {
      params: { distributor_id: distributorId },
    })
    return data
  },

  async remove(id: string): Promise<APIResponse<{ message: string }>> {
    const { data } = await apiClient.delete<APIResponse<{ message: string }>>(`/orders/${id}`)
    return data
  },
}
