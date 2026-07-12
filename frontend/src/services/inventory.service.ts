import apiClient from '@/services/api-client'
import type {
  APIResponse,
  Inventory,
  InventoryAdjustPayload,
  InventoryCreatePayload,
  InventoryDashboard,
  InventoryTransferPayload,
  PaginatedResponse,
  StockMovement,
  Warehouse,
  WarehouseCreatePayload,
  WarehouseUpdatePayload,
} from '@/types'

export interface InventoryQuery {
  page?: number
  page_size?: number
  search?: string
  brand?: string
  category_id?: string
  warehouse_id?: string
  status?: string
}

export interface StockMovementQuery {
  page?: number
  page_size?: number
  inventory_id?: string
}

export const inventoryService = {
  async list(params: InventoryQuery = {}): Promise<PaginatedResponse<Inventory>> {
    const { data } = await apiClient.get<PaginatedResponse<Inventory>>('/inventory', { params })
    return data
  },

  async get(id: string): Promise<APIResponse<Inventory>> {
    const { data } = await apiClient.get<APIResponse<Inventory>>(`/inventory/${id}`)
    return data
  },

  async create(payload: InventoryCreatePayload): Promise<APIResponse<Inventory>> {
    const { data } = await apiClient.post<APIResponse<Inventory>>('/inventory', payload)
    return data
  },

  async adjust(id: string, payload: InventoryAdjustPayload): Promise<APIResponse<Inventory>> {
    const { data } = await apiClient.put<APIResponse<Inventory>>(`/inventory/${id}/adjust`, payload)
    return data
  },

  async transfer(id: string, payload: InventoryTransferPayload): Promise<APIResponse<Inventory>> {
    const { data } = await apiClient.put<APIResponse<Inventory>>(`/inventory/${id}/transfer`, payload)
    return data
  },

  async dashboard(): Promise<APIResponse<InventoryDashboard>> {
    const { data } = await apiClient.get<APIResponse<InventoryDashboard>>('/inventory/dashboard')
    return data
  },

  async listMovements(params: StockMovementQuery = {}): Promise<PaginatedResponse<StockMovement>> {
    const { data } = await apiClient.get<PaginatedResponse<StockMovement>>('/inventory/movements', { params })
    return data
  },

  async listWarehouses(): Promise<APIResponse<Warehouse[]>> {
    const { data } = await apiClient.get<APIResponse<Warehouse[]>>('/inventory/warehouses')
    return data
  },

  async createWarehouse(payload: WarehouseCreatePayload): Promise<APIResponse<Warehouse>> {
    const { data } = await apiClient.post<APIResponse<Warehouse>>('/inventory/warehouses', payload)
    return data
  },

  async updateWarehouse(id: string, payload: WarehouseUpdatePayload): Promise<APIResponse<Warehouse>> {
    const { data } = await apiClient.put<APIResponse<Warehouse>>(`/inventory/warehouses/${id}`, payload)
    return data
  },
}
