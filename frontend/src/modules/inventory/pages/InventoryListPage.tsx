import { AlertTriangle, Boxes, IndianRupee, Package, Plus, Search, Warehouse } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { inventoryService } from '@/services/inventory.service'
import type { Inventory, InventoryDashboard, Warehouse as WarehouseType } from '@/types'

const statusStyles: Record<string, string> = {
  in_stock: 'bg-emerald-100 text-emerald-800',
  low_stock: 'bg-amber-100 text-amber-800',
  out_of_stock: 'bg-rose-100 text-rose-800',
  over_stock: 'bg-sky-100 text-sky-800',
  reserved: 'bg-violet-100 text-violet-800',
}

export function InventoryListPage() {
  const [inventory, setInventory] = useState<Inventory[]>([])
  const [warehouses, setWarehouses] = useState<WarehouseType[]>([])
  const [dashboard, setDashboard] = useState<InventoryDashboard | null>(null)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [warehouseId, setWarehouseId] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    void inventoryService.listWarehouses().then((response) => setWarehouses(response.data ?? []))
    void inventoryService.dashboard().then((response) => setDashboard(response.data ?? null))
  }, [])

  useEffect(() => {
    const loadInventory = async () => {
      setIsLoading(true)
      try {
        const response = await inventoryService.list({
          page,
          page_size: 10,
          search: search || undefined,
          status: status || undefined,
          warehouse_id: warehouseId || undefined,
        })
        setInventory(response.data ?? [])
        setTotalPages(response.total_pages)
      } finally {
        setIsLoading(false)
      }
    }

    void loadInventory()
  }, [page, search, status, warehouseId])

  const summaryCards = dashboard
    ? [
        { label: 'Inventory Items', value: dashboard.total_inventory_items, icon: Boxes, tone: 'text-neutral-700' },
        { label: 'Low Stock', value: dashboard.low_stock_items, icon: AlertTriangle, tone: 'text-amber-600' },
        { label: 'Critical Stock', value: dashboard.critical_stock_items, icon: AlertTriangle, tone: 'text-orange-600' },
        { label: 'Out of Stock', value: dashboard.out_of_stock_items, icon: Package, tone: 'text-rose-600' },
        { label: 'Inventory Value', value: `₹${Number(dashboard.inventory_value || 0).toLocaleString('en-IN')}`, icon: IndianRupee, tone: 'text-emerald-600' },
      ]
    : []

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Inventory</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Monitor stock availability, reservations, and dispatch impact.</p>
        </div>
        <Link
          to="/inventory/new"
          className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700"
        >
          <Plus className="h-4 w-4" />
          New Inventory Record
        </Link>
      </div>

      {dashboard && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {summaryCards.map((card) => (
            <div key={card.label} className="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark">
              <div className={`flex items-center gap-2 text-xs font-semibold uppercase tracking-wide text-neutral-500`}>
                <card.icon className={`h-4 w-4 ${card.tone}`} />
                {card.label}
              </div>
              <p className={`mt-2 text-xl font-semibold ${card.tone}`}>{card.value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark md:grid-cols-[1fr_200px_200px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          <input
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
            placeholder="Search SKU or product"
            className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-10 pr-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
        </div>
        <select
          value={warehouseId}
          onChange={(event) => {
            setWarehouseId(event.target.value)
            setPage(1)
          }}
          className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        >
          <option value="">All Warehouses</option>
          {warehouses.map((warehouse) => (
            <option key={warehouse.id} value={warehouse.id}>
              {warehouse.name}
            </option>
          ))}
        </select>
        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value)
            setPage(1)
          }}
          className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        >
          <option value="">All Status</option>
          <option value="in_stock">In Stock</option>
          <option value="low_stock">Low Stock</option>
          <option value="out_of_stock">Out of Stock</option>
          <option value="over_stock">Over Stock</option>
          <option value="reserved">Reserved</option>
        </select>
      </div>

      <div className="flex flex-wrap gap-2">
        {[
          { label: 'Low Stock Only', value: 'low_stock' },
          { label: 'Out of Stock', value: 'out_of_stock' },
        ].map((quick) => (
          <button
            key={quick.value}
            type="button"
            onClick={() => {
              setStatus((current) => (current === quick.value ? '' : quick.value))
              setPage(1)
            }}
            className={`h-8 rounded-full border px-3 text-xs font-semibold transition ${
              status === quick.value
                ? 'border-primary-600 bg-primary-50 text-primary-700 dark:bg-primary-900/30'
                : 'border-neutral-200 text-neutral-600 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300'
            }`}
          >
            {quick.label}
          </button>
        ))}
      </div>

      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        <div className="hidden grid-cols-[1.4fr_1fr_1fr_1fr_140px] gap-4 border-b border-neutral-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-neutral-500 md:grid">
          <span>Item</span>
          <span>Warehouse</span>
          <span>Stock</span>
          <span>Value</span>
          <span>Status</span>
        </div>
        {isLoading ? (
          <div className="p-6 text-sm text-neutral-600">Loading inventory...</div>
        ) : inventory.length === 0 ? (
          <div className="p-6 text-sm text-neutral-600">No inventory records found.</div>
        ) : (
          inventory.map((item) => (
            <div key={item.id} className="grid gap-3 border-b border-neutral-100 px-4 py-4 last:border-0 md:grid-cols-[1.4fr_1fr_1fr_1fr_140px] md:items-center">
              <div>
                <Link to={`/inventory/${item.id}`} className="font-semibold text-neutral-900 hover:text-primary-600 dark:text-neutral-50">
                  {item.product_name || item.sku || 'Inventory item'}
                </Link>
                <p className="text-xs text-neutral-500">{item.sku} · {item.category || 'Uncategorized'}</p>
              </div>
              <div className="flex items-center gap-2 text-sm text-neutral-700 dark:text-neutral-300">
                <Warehouse className="h-4 w-4 text-neutral-400" />
                {item.warehouse_name || 'Warehouse'}
              </div>
              <div className="text-sm text-neutral-700 dark:text-neutral-300">
                <div className="flex items-center gap-1">
                  {item.current_stock <= 0 && <AlertTriangle className="h-4 w-4 text-rose-500" />}
                  {item.current_stock} available
                </div>
                <div className="text-xs text-neutral-500">Reserved: {item.reserved_stock} · Dispatched: {item.dispatched_stock}</div>
                {item.reorder_quantity > 0 && (
                  <div className="text-xs font-medium text-amber-600">Reorder {item.reorder_quantity} units</div>
                )}
              </div>
              <div className="text-sm text-neutral-700 dark:text-neutral-300">₹{Number(item.inventory_value || 0).toLocaleString('en-IN')}</div>
              <span className={`inline-flex w-fit items-center rounded px-2 py-1 text-xs font-medium capitalize ${statusStyles[item.status] || 'bg-neutral-100 text-neutral-700'}`}>
                {item.status.replace('_', ' ')}
              </span>
            </div>
          ))
        )}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-neutral-500">Page {page} of {Math.max(totalPages, 1)}</p>
        <div className="flex gap-2">
          <button type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Previous</button>
          <button type="button" disabled={totalPages === 0 || page >= totalPages} onClick={() => setPage((value) => value + 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Next</button>
        </div>
      </div>
    </div>
  )
}
