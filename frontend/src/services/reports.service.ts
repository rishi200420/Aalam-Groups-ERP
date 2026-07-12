import apiClient from '@/services/api-client'
import type {
  APIResponse,
  DeadStockReport,
  DispatchReport,
  InventoryReport,
  LowStockReport,
  OrderReport,
  OutletReport,
  ReportType,
  SalesReport,
  StockMovementReport,
  TopSellingReport,
  WarehouseReport,
} from '@/types'

export interface ReportFilters {
  start_date?: string
  end_date?: string
  brand?: string
  warehouse_id?: string
  status?: string
  movement_type?: string
  threshold_days?: number
  limit?: number
}

function cleanParams(filters: ReportFilters): Record<string, string | number> {
  const params: Record<string, string | number> = {}
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '') params[key] = value
  })
  return params
}

export const reportsService = {
  async sales(filters: ReportFilters = {}): Promise<APIResponse<SalesReport>> {
    const { data } = await apiClient.get<APIResponse<SalesReport>>('/reports/sales', { params: cleanParams(filters) })
    return data
  },
  async inventory(filters: ReportFilters = {}): Promise<APIResponse<InventoryReport>> {
    const { data } = await apiClient.get<APIResponse<InventoryReport>>('/reports/inventory', { params: cleanParams(filters) })
    return data
  },
  async stockMovements(filters: ReportFilters = {}): Promise<APIResponse<StockMovementReport>> {
    const { data } = await apiClient.get<APIResponse<StockMovementReport>>('/reports/stock-movements', { params: cleanParams(filters) })
    return data
  },
  async dispatch(filters: ReportFilters = {}): Promise<APIResponse<DispatchReport>> {
    const { data } = await apiClient.get<APIResponse<DispatchReport>>('/reports/dispatch', { params: cleanParams(filters) })
    return data
  },
  async orders(filters: ReportFilters = {}): Promise<APIResponse<OrderReport>> {
    const { data } = await apiClient.get<APIResponse<OrderReport>>('/reports/orders', { params: cleanParams(filters) })
    return data
  },
  async outlets(filters: ReportFilters = {}): Promise<APIResponse<OutletReport>> {
    const { data } = await apiClient.get<APIResponse<OutletReport>>('/reports/outlets', { params: cleanParams(filters) })
    return data
  },
  async warehouses(): Promise<APIResponse<WarehouseReport>> {
    const { data } = await apiClient.get<APIResponse<WarehouseReport>>('/reports/warehouses')
    return data
  },
  async topSelling(filters: ReportFilters = {}): Promise<APIResponse<TopSellingReport>> {
    const { data } = await apiClient.get<APIResponse<TopSellingReport>>('/reports/top-selling', { params: cleanParams(filters) })
    return data
  },
  async lowStock(filters: ReportFilters = {}): Promise<APIResponse<LowStockReport>> {
    const { data } = await apiClient.get<APIResponse<LowStockReport>>('/reports/low-stock', { params: cleanParams(filters) })
    return data
  },
  async deadStock(filters: ReportFilters = {}): Promise<APIResponse<DeadStockReport>> {
    const { data } = await apiClient.get<APIResponse<DeadStockReport>>('/reports/dead-stock', { params: cleanParams(filters) })
    return data
  },

  async exportCsv(report: ReportType, filters: ReportFilters = {}): Promise<void> {
    const response = await apiClient.get('/reports/export', {
      params: { report, ...cleanParams(filters) },
      responseType: 'blob',
    })
    const disposition = response.headers['content-disposition'] as string | undefined
    const match = disposition?.match(/filename="?([^"]+)"?/)
    const filename = match?.[1] ?? `${report}-report.csv`
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  },
}
