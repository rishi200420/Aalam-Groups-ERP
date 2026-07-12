import { Save } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { categoryService, productService } from '@/services/product.service'
import type { Category, ProductBrand, ProductPayload, ProductStatus } from '@/types'

const emptyForm: ProductPayload = {
  sku: '',
  barcode: '',
  name: '',
  description: '',
  category_id: null,
  brand: 'TASTIQ',
  unit: 'pcs',
  mrp: '',
  distributor_price: '',
  stock_quantity: 0,
  low_stock_threshold: 10,
  status: 'active',
}

export function ProductFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = Boolean(id)
  const [form, setForm] = useState<ProductPayload>(emptyForm)
  const [categories, setCategories] = useState<Category[]>([])
  const [isLoading, setIsLoading] = useState(isEdit)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    void categoryService.list(true).then((response) => setCategories(response.data ?? []))
  }, [])

  useEffect(() => {
    if (!id) return
    void productService
      .get(id)
      .then((response) => {
        if (response.data) {
          const product = response.data
          setForm({
            sku: product.sku,
            barcode: product.barcode ?? '',
            name: product.name,
            description: product.description ?? '',
            category_id: product.category_id ?? null,
            brand: product.brand,
            unit: product.unit,
            mrp: product.mrp,
            distributor_price: product.distributor_price,
            stock_quantity: product.stock_quantity,
            low_stock_threshold: product.low_stock_threshold,
            status: product.status,
          })
        }
      })
      .finally(() => setIsLoading(false))
  }, [id])

  const update = <K extends keyof ProductPayload>(key: K, value: ProductPayload[K]) => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setIsSaving(true)
    setError(null)
    try {
      const payload = { ...form, category_id: form.category_id || null, barcode: form.barcode || null }
      const response = id ? await productService.update(id, payload) : await productService.create(payload)
      if (!response.data) throw new Error(response.message)
      navigate('/products', { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save product.')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm">Loading product...</div>
  }

  return (
    <form onSubmit={(event) => void submit(event)} className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">
            {isEdit ? 'Edit Product' : 'Add Product'}
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Manage SKU, pricing, and stock details.</p>
        </div>
        <button type="submit" disabled={isSaving} className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60">
          <Save className="h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save Product'}
        </button>
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 gap-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark md:grid-cols-2">
        <Input label="SKU" value={form.sku} onChange={(value) => update('sku', value)} required />
        <Input label="Barcode" value={form.barcode ?? ''} onChange={(value) => update('barcode', value)} />
        <Input label="Product Name" value={form.name} onChange={(value) => update('name', value)} required />
        <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Category
          <select value={form.category_id ?? ''} onChange={(event) => update('category_id', event.target.value || null)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
            <option value="">Uncategorized</option>
            {categories.map((category) => <option key={category.id} value={category.id}>{category.name}</option>)}
          </select>
        </label>
        <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Brand
          <select value={form.brand} onChange={(event) => update('brand', event.target.value as ProductBrand)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
            <option value="TASTIQ">TASTIQ</option>
            <option value="LEMURIA">LEMURIA</option>
          </select>
        </label>
        <Input label="Unit" value={form.unit} onChange={(value) => update('unit', value)} required />
        <Input label="MRP (₹)" type="number" value={form.mrp} onChange={(value) => update('mrp', value)} required />
        <Input label="Distributor Price (₹)" type="number" value={form.distributor_price} onChange={(value) => update('distributor_price', value)} required />
        <Input label="Stock Quantity" type="number" value={form.stock_quantity} onChange={(value) => update('stock_quantity', Number(value))} required />
        <Input label="Low Stock Threshold" type="number" value={form.low_stock_threshold} onChange={(value) => update('low_stock_threshold', Number(value))} required />
        <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Status
          <select value={form.status} onChange={(event) => update('status', event.target.value as ProductStatus)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="discontinued">Discontinued</option>
          </select>
        </label>
        <label className="md:col-span-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Description
          <textarea value={form.description ?? ''} onChange={(event) => update('description', event.target.value)} className="mt-1.5 min-h-24 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
        </label>
      </div>
    </form>
  )
}

interface InputProps {
  label: string
  value: string | number
  onChange: (value: string) => void
  type?: string
  required?: boolean
}

function Input({ label, value, onChange, type = 'text', required = false }: InputProps) {
  return (
    <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
      {label}
      <input required={required} type={type} value={value} onChange={(event) => onChange(event.target.value)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
    </label>
  )
}
