import { ArrowLeft, Plus, Save } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { inventoryService } from '@/services/inventory.service'
import { productService } from '@/services/product.service'
import type { InventoryCreatePayload, Product, Warehouse, WarehouseCreatePayload } from '@/types'

const emptyForm: InventoryCreatePayload = {
  product_id: '',
  warehouse_id: '',
  opening_stock: 0,
  available_stock: 0,
  reserved_stock: 0,
  dispatched_stock: 0,
  returned_stock: 0,
  current_stock: 0,
  minimum_stock: 0,
  maximum_stock: 0,
  purchase_cost: 0,
  selling_price: 0,
  notes: '',
}

const emptyWarehouseForm: WarehouseCreatePayload = {
  name: '',
  code: '',
  address: '',
  contact_person: '',
  phone: '',
  is_default: false,
  is_active: true,
}

export function InventoryFormPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState<InventoryCreatePayload>(emptyForm)
  const [products, setProducts] = useState<Product[]>([])
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [showWarehouseForm, setShowWarehouseForm] = useState(false)
  const [warehouseForm, setWarehouseForm] = useState<WarehouseCreatePayload>(emptyWarehouseForm)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadWarehouses = async () => {
    const response = await inventoryService.listWarehouses()
    setWarehouses(response.data ?? [])
  }

  useEffect(() => {
    void productService.list({ page: 1, page_size: 100 }).then((response) => setProducts(response.data ?? []))
    void loadWarehouses()
  }, [])

  const update = <K extends keyof InventoryCreatePayload>(key: K, value: InventoryCreatePayload[K]) => {
    setForm((current) => {
      const next = { ...current, [key]: value }
      if (key === 'opening_stock') {
        next.available_stock = Number(value)
        next.current_stock = Number(value)
      }
      return next
    })
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    if (!form.product_id || !form.warehouse_id) {
      setError('Select a product and a warehouse before saving.')
      return
    }
    setIsSaving(true)
    setError(null)
    try {
      const response = await inventoryService.create({
        ...form,
        notes: form.notes || undefined,
      })
      if (!response.data) throw new Error(response.message)
      navigate(`/inventory/${response.data.id}`, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create inventory record.')
    } finally {
      setIsSaving(false)
    }
  }

  const createWarehouse = async (event: FormEvent) => {
    event.preventDefault()
    if (!warehouseForm.name || !warehouseForm.code) {
      setError('Warehouse name and code are required.')
      return
    }
    setIsSaving(true)
    setError(null)
    try {
      const response = await inventoryService.createWarehouse(warehouseForm)
      if (!response.data) throw new Error(response.message)
      await loadWarehouses()
      update('warehouse_id', response.data.id)
      setShowWarehouseForm(false)
      setWarehouseForm(emptyWarehouseForm)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create warehouse.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <Link to="/inventory" className="inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700">
          <ArrowLeft className="h-4 w-4" />
          Back to inventory
        </Link>
        <h2 className="mt-2 text-2xl font-semibold text-neutral-900 dark:text-neutral-50">New Inventory Record</h2>
        <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">Set up opening stock for a product at a warehouse.</p>
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      <form onSubmit={submit} className="space-y-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Product</label>
            <select
              required
              value={form.product_id}
              onChange={(event) => update('product_id', event.target.value)}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            >
              <option value="">Select product</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name} ({product.sku})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Warehouse</label>
            <div className="mt-1 flex gap-2">
              <select
                required
                value={form.warehouse_id}
                onChange={(event) => update('warehouse_id', event.target.value)}
                className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              >
                <option value="">Select warehouse</option>
                {warehouses.map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name} ({warehouse.code})
                  </option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => setShowWarehouseForm((value) => !value)}
                className="inline-flex h-10 items-center gap-1 rounded-lg border border-neutral-200 px-3 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300"
              >
                <Plus className="h-4 w-4" />
                New
              </button>
            </div>
          </div>
        </div>

        {showWarehouseForm && (
          <div className="space-y-3 rounded-lg border border-dashed border-neutral-300 p-4 dark:border-neutral-700">
            <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-50">Quick-add warehouse</p>
            <div className="grid gap-3 sm:grid-cols-2">
              <input
                placeholder="Warehouse name"
                value={warehouseForm.name}
                onChange={(event) => setWarehouseForm((current) => ({ ...current, name: event.target.value }))}
                className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
              <input
                placeholder="Code (e.g. WH-02)"
                value={warehouseForm.code}
                onChange={(event) => setWarehouseForm((current) => ({ ...current, code: event.target.value }))}
                className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
              <input
                placeholder="Contact person"
                value={warehouseForm.contact_person}
                onChange={(event) => setWarehouseForm((current) => ({ ...current, contact_person: event.target.value }))}
                className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
              <input
                placeholder="Phone"
                value={warehouseForm.phone}
                onChange={(event) => setWarehouseForm((current) => ({ ...current, phone: event.target.value }))}
                className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
            </div>
            <textarea
              placeholder="Address"
              value={warehouseForm.address}
              onChange={(event) => setWarehouseForm((current) => ({ ...current, address: event.target.value }))}
              className="h-16 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
            <button
              type="button"
              onClick={createWarehouse}
              disabled={isSaving}
              className="h-9 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-60"
            >
              Save warehouse
            </button>
          </div>
        )}

        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Opening stock</label>
            <input
              type="number"
              min={0}
              value={form.opening_stock}
              onChange={(event) => update('opening_stock', Number(event.target.value))}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Minimum stock (reorder level)</label>
            <input
              type="number"
              min={0}
              value={form.minimum_stock}
              onChange={(event) => update('minimum_stock', Number(event.target.value))}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Maximum stock</label>
            <input
              type="number"
              min={0}
              value={form.maximum_stock}
              onChange={(event) => update('maximum_stock', Number(event.target.value))}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Purchase cost (₹)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={form.purchase_cost}
              onChange={(event) => update('purchase_cost', Number(event.target.value))}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Selling price (₹)</label>
            <input
              type="number"
              min={0}
              step="0.01"
              value={form.selling_price}
              onChange={(event) => update('selling_price', Number(event.target.value))}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
        </div>

        <div>
          <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Notes</label>
          <textarea
            value={form.notes}
            onChange={(event) => update('notes', event.target.value)}
            className="mt-1 h-20 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Link to="/inventory" className="inline-flex h-10 items-center rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 dark:border-neutral-700 dark:text-neutral-300">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={isSaving}
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-60"
          >
            <Save className="h-4 w-4" />
            {isSaving ? 'Saving...' : 'Create inventory record'}
          </button>
        </div>
      </form>
    </div>
  )
}
