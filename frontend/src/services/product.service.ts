import apiClient from '@/services/api-client'
import type {
  APIResponse,
  Category,
  CategoryPayload,
  PaginatedResponse,
  Product,
  ProductPayload,
  ProductSummary,
} from '@/types'

export interface ProductQuery {
  page?: number
  page_size?: number
  search?: string
  category_id?: string
  brand?: string
  status?: string
  low_stock_only?: boolean
}

export const productService = {
  async list(params: ProductQuery = {}): Promise<PaginatedResponse<Product>> {
    const { data } = await apiClient.get<PaginatedResponse<Product>>('/products', { params })
    return data
  },

  async summary(): Promise<APIResponse<ProductSummary>> {
    const { data } = await apiClient.get<APIResponse<ProductSummary>>('/products/summary')
    return data
  },

  async get(id: string): Promise<APIResponse<Product>> {
    const { data } = await apiClient.get<APIResponse<Product>>(`/products/${id}`)
    return data
  },

  async create(payload: Partial<ProductPayload>): Promise<APIResponse<Product>> {
    const { data } = await apiClient.post<APIResponse<Product>>('/products', payload)
    return data
  },

  async update(id: string, payload: Partial<ProductPayload>): Promise<APIResponse<Product>> {
    const { data } = await apiClient.patch<APIResponse<Product>>(`/products/${id}`, payload)
    return data
  },

  async remove(id: string): Promise<APIResponse<{ message: string }>> {
    const { data } = await apiClient.delete<APIResponse<{ message: string }>>(`/products/${id}`)
    return data
  },

  async adjustStock(id: string, quantity: number, reason: string): Promise<APIResponse<Product>> {
    const { data } = await apiClient.post<APIResponse<Product>>(`/products/${id}/stock-adjustments`, {
      quantity,
      reason,
    })
    return data
  },

  async uploadImage(id: string, file: File, isPrimary = false): Promise<APIResponse<Product>> {
    const form = new FormData()
    form.append('file', file)
    const { data } = await apiClient.post<APIResponse<Product>>(`/products/${id}/images`, form, {
      params: { is_primary: isPrimary },
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },
}

export const categoryService = {
  async list(isActive?: boolean): Promise<APIResponse<Category[]>> {
    const { data } = await apiClient.get<APIResponse<Category[]>>('/products/categories', {
      params: isActive === undefined ? {} : { is_active: isActive },
    })
    return data
  },

  async create(payload: CategoryPayload): Promise<APIResponse<Category>> {
    const { data } = await apiClient.post<APIResponse<Category>>('/products/categories', payload)
    return data
  },

  async update(id: string, payload: Partial<CategoryPayload>): Promise<APIResponse<Category>> {
    const { data } = await apiClient.patch<APIResponse<Category>>(`/products/categories/${id}`, payload)
    return data
  },

  async remove(id: string): Promise<APIResponse<{ message: string }>> {
    const { data } = await apiClient.delete<APIResponse<{ message: string }>>(`/products/categories/${id}`)
    return data
  },
}
