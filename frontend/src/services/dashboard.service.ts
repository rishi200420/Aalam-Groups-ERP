import apiClient from '@/services/api-client'
import type { APIResponse, BrandFilter, DashboardStats } from '@/types'

export const dashboardService = {
  async getStats(brand: BrandFilter = 'all'): Promise<APIResponse<DashboardStats>> {
    const { data } = await apiClient.get<APIResponse<DashboardStats>>('/analytics/dashboard', {
      params: brand === 'all' ? {} : { brand },
    })
    return data
  },
}
