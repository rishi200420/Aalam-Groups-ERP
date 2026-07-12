import { Plus, Save, Trash2 } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { orderService } from '@/services/order.service'
import { outletService } from '@/services/outlet.service'
import { productService } from '@/services/product.service'
import type { Outlet, OrderItemInput, Product } from '@/types'

interface DraftLine extends OrderItemInput {
  key: string
}

export function OrderFormPage() {
  const navigate = useNavigate()
  const [outlets, setOutlets] = useState<Outlet[]>([])
  const [products, setProducts] = useState<Product[]>([])
  const [outletId, setOutletId] = useState('')
  const [notes, setNotes] = useState('')
  const [lines, setLines] = useState<DraftLine[]>([{ key: crypto.randomUUID(), product_id: '', quantity: 1 }])
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    void outletService.list({ page: 1, page_size: 100 }).then((response) => setOutlets(response.data ?? []))
    void productService.list({ page: 1, page_size: 100, status: 'active' }).then((response) => setProducts(response.data ?? []))
  }, [])

  const productById = (id: string) => products.find((product) => product.id === id)

  const updateLine = (key: string, patch: Partial<DraftLine>) => {
    setLines((current) => current.map((line) => (line.key === key ? { ...line, ...patch } : line)))
  }

  const addLine = () => setLines((current) => [...current, { key: crypto.randomUUID(), product_id: '', quantity: 1 }])
  const removeLine = (key: string) => setLines((current) => current.filter((line) => line.key !== key))

  const total = lines.reduce((sum, line) => {
    const product = productById(line.product_id)
    return sum + (product ? Number(product.distributor_price) * line.quantity : 0)
  }, 0)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    const items = lines.filter((line) => line.product_id && line.quantity > 0).map(({ product_id, quantity }) => ({ product_id, quantity }))
    if (!outletId) {
      setError('Please select an outlet.')
      return
    }
    if (items.length === 0) {
      setError('Add at least one product line.')
      return
    }
    setIsSaving(true)
    try {
      const response = await orderService.create({ outlet_id: outletId, notes: notes || undefined, items })
      if (!response.data) throw new Error(response.message)
      navigate(`/orders/${response.data.id}`, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to create order.')
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <form onSubmit={(event) => void submit(event)} className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Create Order</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Select an outlet and add products to build the order.</p>
        </div>
        <button type="submit" disabled={isSaving} className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60">
          <Save className="h-4 w-4" />
          {isSaving ? 'Placing order...' : 'Place Order'}
        </button>
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Outlet
          <select required value={outletId} onChange={(event) => setOutletId(event.target.value)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
            <option value="">Select an outlet</option>
            {outlets.map((outlet) => <option key={outlet.id} value={outlet.id}>{outlet.shop_name} — {outlet.area}</option>)}
          </select>
        </label>
      </div>

      <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Order Items</h3>
          <button type="button" onClick={addLine} className="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700">
            <Plus className="h-4 w-4" /> Add line
          </button>
        </div>
        <div className="space-y-3">
          {lines.map((line) => {
            const product = productById(line.product_id)
            return (
              <div key={line.key} className="grid grid-cols-1 gap-2 sm:grid-cols-[1fr_120px_120px_40px] sm:items-center">
                <select value={line.product_id} onChange={(event) => updateLine(line.key, { product_id: event.target.value })} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
                  <option value="">Select product</option>
                  {products.map((p) => <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>)}
                </select>
                <input type="number" min={1} value={line.quantity} onChange={(event) => updateLine(line.key, { quantity: Number(event.target.value) })} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
                <div className="text-sm text-neutral-600 dark:text-neutral-400">
                  {product ? `₹${(Number(product.distributor_price) * line.quantity).toFixed(2)}` : '—'}
                </div>
                <button type="button" onClick={() => removeLine(line.key)} className="rounded-lg border border-red-200 p-2 text-red-600 hover:bg-red-50">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            )
          })}
        </div>
        <div className="mt-4 flex justify-end border-t border-neutral-100 pt-3 text-sm font-semibold text-neutral-900 dark:border-neutral-800 dark:text-neutral-50">
          Total: ₹{total.toFixed(2)}
        </div>
      </div>

      <label className="block rounded-lg border border-neutral-200 bg-white p-5 text-sm font-medium text-neutral-700 dark:border-neutral-800 dark:bg-surface-dark dark:text-neutral-300">
        Notes
        <textarea value={notes} onChange={(event) => setNotes(event.target.value)} className="mt-1.5 min-h-20 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
      </label>
    </form>
  )
}
