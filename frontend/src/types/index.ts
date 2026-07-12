export type UserRole = 'super_admin' | 'founder' | 'distributor' | 'warehouse' | 'sales_executive'

export interface User {
  id: string
  full_name: string
  email: string
  phone?: string
  roles: UserRole[]
  primary_role?: UserRole | null
  is_active: boolean
}

export interface APIResponse<T = unknown> {
  success: boolean
  message: string
  data: T | null
}

export interface PaginatedResponse<T> extends APIResponse<T[]> {
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginResponse extends AuthTokens {
  user: User
}

export interface Territory {
  id: string
  code: string
  name: string
  region?: string
  is_active: boolean
}

export interface Brand {
  id: string
  name: string
  code: string
  is_active: boolean
}

export type BusinessType =
  | 'tea_shop'
  | 'cafe'
  | 'bakery'
  | 'restaurant'
  | 'hotel'
  | 'supermarket'
  | 'general_store'

export type OutletStatus = 'active' | 'inactive' | 'blocked'
export type OutletBrand = 'TASTIQ' | 'LEMURIA'
export type OutletPhotoType = 'shop_front' | 'inside_shop' | 'name_board'

export interface OutletVisit {
  id: string
  visit_date: string
  distributor_id?: string | null
  latitude?: number | null
  longitude?: number | null
  photo_url?: string | null
  notes?: string | null
  next_follow_up_date?: string | null
  created_at: string
}

export interface OutletPhoto {
  id: string
  photo_type: OutletPhotoType
  file_name: string
  file_url: string
  content_type?: string | null
  size_bytes?: number | null
  created_at: string
}

export interface OutletContact {
  id: string
  name: string
  role?: string | null
  phone?: string | null
  whatsapp?: string | null
  email?: string | null
}

export interface Outlet {
  id: string
  outlet_id: string
  shop_name: string
  owner_name: string
  phone_number: string
  whatsapp_number?: string | null
  email?: string | null
  gst_number?: string | null
  address: string
  area: string
  city: string
  district: string
  state: string
  pincode: string
  territory: string
  latitude?: number | null
  longitude?: number | null
  google_maps_url?: string | null
  business_type: BusinessType
  brands: OutletBrand[]
  assigned_distributor_id?: string | null
  assigned_distributor?: User | null
  status: OutletStatus
  notes?: string | null
  qr_code_value: string
  qr_code_url: string
  visits: OutletVisit[]
  photos: OutletPhoto[]
  contacts: OutletContact[]
  created_at: string
  updated_at: string
}

export interface OutletSummary {
  total: number
  active: number
  new_this_month: number
  visits_today: number
}

export type OutletPayload = Omit<
  Outlet,
  | 'id'
  | 'outlet_id'
  | 'assigned_distributor'
  | 'qr_code_value'
  | 'qr_code_url'
  | 'visits'
  | 'photos'
  | 'contacts'
  | 'created_at'
  | 'updated_at'
> & {
  contacts?: Array<Omit<OutletContact, 'id'>>
}

export type ProductBrand = 'TASTIQ' | 'LEMURIA'
export type ProductStatus = 'active' | 'inactive' | 'discontinued'

export interface Category {
  id: string
  name: string
  code: string
  description?: string | null
  is_active: boolean
  product_count: number
  created_at: string
  updated_at: string
}

export type CategoryPayload = Omit<Category, 'id' | 'product_count' | 'created_at' | 'updated_at'>

export interface ProductImage {
  id: string
  file_name: string
  file_url: string
  content_type?: string | null
  size_bytes?: number | null
  is_primary: boolean
  created_at: string
}

export interface Product {
  id: string
  sku: string
  barcode?: string | null
  name: string
  description?: string | null
  category_id?: string | null
  category?: Category | null
  brand: ProductBrand
  unit: string
  mrp: string
  distributor_price: string
  stock_quantity: number
  low_stock_threshold: number
  is_low_stock: boolean
  status: ProductStatus
  images: ProductImage[]
  created_at: string
  updated_at: string
}

export type ProductPayload = Omit<
  Product,
  'id' | 'category' | 'is_low_stock' | 'images' | 'created_at' | 'updated_at'
>

export interface ProductSummary {
  total: number
  active: number
  low_stock: number
  out_of_stock: number
}

export interface ManagedUser {
  id: string
  email: string
  full_name: string
  phone?: string | null
  role: UserRole
  is_active: boolean
  employee_id?: string | null
  distributor_code?: string | null
  territory?: string | null
  brand?: ProductBrand | null
  joining_date?: string | null
  profile_image_url?: string | null
  last_login_at?: string | null
  created_at: string
  updated_at: string
}

export interface ManagedUserCreatePayload {
  full_name: string
  email: string
  phone?: string
  password: string
  role: UserRole
  employee_id?: string
  distributor_code?: string
  territory?: string
  brand?: ProductBrand
  joining_date?: string
}

export type ManagedUserUpdatePayload = Partial<Omit<ManagedUserCreatePayload, 'email' | 'password'>> & {
  is_active?: boolean
}

export type OrderStatus = 'pending' | 'approved' | 'packed' | 'dispatched' | 'delivered' | 'cancelled'

export interface OrderItem {
  id: string
  product_id: string
  product?: Product | null
  quantity: number
  unit_price: string
  line_total: string
}

export interface OrderStatusHistoryEntry {
  id: string
  status: string
  notes?: string | null
  changed_by?: string | null
  changed_at: string
}

export interface Order {
  id: string
  order_number: string
  outlet_id: string
  outlet_name: string
  distributor_id?: string | null
  distributor_name?: string | null
  status: OrderStatus
  subtotal: string
  total_amount: string
  notes?: string | null
  stock_deducted: boolean
  cancelled_reason?: string | null
  items: OrderItem[]
  status_history: OrderStatusHistoryEntry[]
  created_at: string
  updated_at: string
}

export interface OrderItemInput {
  product_id: string
  quantity: number
}

export interface OrderCreatePayload {
  outlet_id: string
  distributor_id?: string | null
  notes?: string
  items: OrderItemInput[]
}

export interface OrderSummary {
  total: number
  pending: number
  approved: number
  dispatched_today: number
  delivered_today: number
  revenue_today: string
}

export interface DashboardRecentOrder {
  id: string
  order_number: string
  outlet_name: string
  distributor_name?: string | null
  brands: string[]
  product_summary: string
  status: OrderStatus
  total_amount: string
  created_at: string
}

export interface DashboardTopProduct {
  product_id: string
  name: string
  sku: string
  brand: string
  units_sold: number
  revenue: string
}

export interface DashboardActivity {
  type: string
  message: string
  created_at: string
}

export type DispatchStatus = 'ready' | 'dispatched' | 'in_transit' | 'delivered' | 'failed' | 'returned'

export interface DispatchTimelineEntry {
  id: string
  status: string
  notes?: string | null
  changed_by?: string | null
  changed_at: string
}

export interface DispatchItem {
  id: string
  product_id: string
  product?: Product | null
  quantity: number
  unit_price: string
  line_total: string
}

export interface Dispatch {
  id: string
  dispatch_number: string
  order_id: string
  order_number?: string | null
  status: DispatchStatus
  tracking_number?: string | null
  courier_name?: string | null
  notes?: string | null
  items: DispatchItem[]
  timelines: DispatchTimelineEntry[]
  created_at: string
  updated_at: string
}

export interface DispatchItemInput {
  product_id: string
  quantity: number
}

export interface DispatchCreatePayload {
  order_id: string
  tracking_number?: string | null
  courier_name?: string | null
  notes?: string | null
  items: DispatchItemInput[]
}

export interface DispatchStatusUpdatePayload {
  status: DispatchStatus
  notes?: string | null
}

export interface Inventory {
  id: string
  product_id: string
  product_name?: string | null
  sku?: string | null
  brand?: string | null
  category?: string | null
  warehouse_id: string
  warehouse_name?: string | null
  opening_stock: number
  available_stock: number
  reserved_stock: number
  dispatched_stock: number
  returned_stock: number
  current_stock: number
  minimum_stock: number
  maximum_stock: number
  purchase_cost: string
  selling_price: string
  inventory_value: string
  status: 'in_stock' | 'low_stock' | 'out_of_stock' | 'over_stock' | 'reserved'
  reorder_quantity: number
  notes?: string | null
  created_at: string
  updated_at: string
}

export interface InventoryCreatePayload {
  product_id: string
  warehouse_id: string
  opening_stock: number
  available_stock: number
  reserved_stock?: number
  dispatched_stock?: number
  returned_stock?: number
  current_stock: number
  minimum_stock: number
  maximum_stock: number
  purchase_cost: number
  selling_price: number
  notes?: string
}

export interface InventoryAdjustPayload {
  quantity: number
  reason: string
  movement_type?: 'adjustment' | 'manual_correction' | 'purchase' | 'damage'
}

export interface InventoryTransferPayload {
  target_warehouse_id: string
  quantity: number
  notes?: string
}

export interface InventoryDashboard {
  total_inventory_items: number
  low_stock_items: number
  critical_stock_items: number
  out_of_stock_items: number
  in_stock_items: number
  reserved_stock: number
  inventory_value: string
  warehouses_count: number
  products_in_stock: number
}

export interface StockMovement {
  id: string
  inventory_id: string
  product_id: string
  warehouse_id: string
  quantity: number
  movement_type: string
  reference?: string | null
  created_by?: string | null
  notes?: string | null
  created_at: string
}

export interface Warehouse {
  id: string
  name: string
  code: string
  address?: string | null
  contact_person?: string | null
  phone?: string | null
  is_default: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface WarehouseCreatePayload {
  name: string
  code: string
  address?: string
  contact_person?: string
  phone?: string
  is_default?: boolean
  is_active?: boolean
}

export type WarehouseUpdatePayload = Partial<WarehouseCreatePayload>

export interface DashboardDispatch {
  pending: number
  completed_today: number
  delayed: number
}

export interface DashboardDailyCount {
  date: string
  count: number
}

export interface DashboardDailyRevenue {
  date: string
  revenue: string
}

export interface DashboardStats {
  brand_filter: string
  orders_today: number
  revenue_today: string
  revenue_mtd: string
  pending_orders: number
  pending_dispatch: number
  delivered_orders_total: number
  low_stock_products: number
  out_of_stock_products: number
  inventory_value: string
  total_products: number
  total_outlets: number
  active_outlets: number
  total_distributors: number
  dispatch: DashboardDispatch
  orders_last_7_days: DashboardDailyCount[]
  revenue_last_30_days: DashboardDailyRevenue[]
  recent_orders: DashboardRecentOrder[]
  top_selling_products: DashboardTopProduct[]
  recent_activities: DashboardActivity[]
}

export type BrandFilter = 'all' | 'tastiq' | 'lemuria'

export function isFounderRole(role?: UserRole | null): boolean {
  return role === 'founder' || role === 'super_admin'
}

export function isDistributorRole(role?: UserRole | null): boolean {
  return role === 'distributor'
}

export function isWarehouseRole(role?: UserRole | null): boolean {
  return role === 'warehouse'
}

export function isSalesExecutiveRole(role?: UserRole | null): boolean {
  return role === 'sales_executive'
}

// --- Reports ---

export interface StatusCount {
  status: string
  count: number
}

export interface BrandSales {
  brand: string
  orders_count: number
  revenue: string
}

export interface DailySales {
  date: string
  orders_count: number
  revenue: string
}

export interface SalesReport {
  start_date: string
  end_date: string
  total_orders: number
  total_revenue: string
  average_order_value: string
  by_status: StatusCount[]
  by_brand: BrandSales[]
  daily: DailySales[]
}

export interface InventoryReportRow {
  product_name: string
  sku: string
  brand?: string | null
  warehouse_name: string
  current_stock: number
  reserved_stock: number
  available_stock: number
  minimum_stock: number
  purchase_cost: string
  inventory_value: string
  status: string
}

export interface InventoryReport {
  total_items: number
  total_value: string
  low_stock_count: number
  out_of_stock_count: number
  rows: InventoryReportRow[]
}

export interface StockMovementReportRow {
  date: string
  product_name: string
  sku: string
  warehouse_name: string
  movement_type: string
  quantity: number
  reference?: string | null
  notes?: string | null
}

export interface StockMovementReport {
  start_date: string
  end_date: string
  total_movements: number
  rows: StockMovementReportRow[]
}

export interface DispatchReportRow {
  dispatch_number: string
  order_number: string
  outlet_name: string
  status: string
  dispatched_at: string
  delivered_at?: string | null
  delivery_hours?: number | null
}

export interface DispatchReport {
  start_date: string
  end_date: string
  total_dispatches: number
  by_status: StatusCount[]
  average_delivery_hours?: number | null
  rows: DispatchReportRow[]
}

export interface OrderReportRow {
  order_number: string
  outlet_name: string
  status: string
  total_amount: string
  created_at: string
}

export interface OrderReport {
  start_date: string
  end_date: string
  total_orders: number
  total_revenue: string
  by_status: StatusCount[]
  rows: OrderReportRow[]
}

export interface OutletReportRow {
  outlet_name: string
  outlet_id: string
  territory: string
  orders_count: number
  revenue: string
  last_order_at?: string | null
}

export interface OutletReport {
  start_date: string
  end_date: string
  rows: OutletReportRow[]
}

export interface WarehouseReportRow {
  warehouse_name: string
  warehouse_code: string
  total_items: number
  total_value: string
  low_stock_count: number
  out_of_stock_count: number
}

export interface WarehouseReport {
  rows: WarehouseReportRow[]
}

export interface TopSellingRow {
  product_name: string
  sku: string
  brand: string
  units_sold: number
  revenue: string
}

export interface TopSellingReport {
  start_date: string
  end_date: string
  rows: TopSellingRow[]
}

export interface LowStockReportRow {
  product_name: string
  sku: string
  warehouse_name: string
  current_stock: number
  minimum_stock: number
  reorder_quantity: number
  status: string
}

export interface LowStockReport {
  rows: LowStockReportRow[]
}

export interface DeadStockRow {
  product_name: string
  sku: string
  warehouse_name: string
  current_stock: number
  inventory_value: string
  last_movement_at?: string | null
  days_since_movement?: number | null
}

export interface DeadStockReport {
  threshold_days: number
  rows: DeadStockRow[]
}

export type ReportType =
  | 'sales'
  | 'inventory'
  | 'stock-movements'
  | 'dispatch'
  | 'orders'
  | 'outlets'
  | 'warehouses'
  | 'top-selling'
  | 'low-stock'
  | 'dead-stock'

// --- Notifications ---

export interface MessageResponse {
  message: string
}

export interface Notification {
  id: string
  type: string
  title: string
  message: string
  reference_type?: string | null
  reference_id?: string | null
  link?: string | null
  is_read: boolean
  read_at?: string | null
  created_at: string
}

export interface NotificationSummary {
  unread_count: number
}

// --- Settings ---

export interface SystemSettings {
  business_name: string
  support_email?: string | null
  support_phone?: string | null
  address?: string | null
  gst_number?: string | null
  default_currency: string
  low_stock_default_threshold: number
  invoice_footer_note?: string | null
}

export type SystemSettingsUpdatePayload = Partial<SystemSettings>

export interface NotificationPreference {
  notify_orders: boolean
  notify_dispatch: boolean
  notify_stock: boolean
  notify_system: boolean
}

export type NotificationPreferenceUpdatePayload = Partial<NotificationPreference>

// --- Profile ---

export interface Profile {
  id: string
  email: string
  full_name: string
  phone?: string | null
  roles: UserRole[]
  primary_role?: UserRole | null
  is_active: boolean
  employee_id?: string | null
  distributor_code?: string | null
  territory?: string | null
  brand?: string | null
  joining_date?: string | null
  profile_image_url?: string | null
  last_login_at?: string | null
  created_at: string
}

export interface ProfileUpdatePayload {
  full_name?: string
  phone?: string
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}
