import { Plus } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { dispatchService } from '@/services/dispatch.service'

export function CreateDispatchPage() {
  const navigate = useNavigate()
  const [orderId, setOrderId] = useState('')
  const [trackingNumber, setTrackingNumber] = useState('')
  const [courierName, setCourierName] = useState('')
  const [notes, setNotes] = useState('')
  const [items, setItems] = useState([{ product_id: '', quantity: 1 }])
  const [error, setError] = useState<string | null>(null)

  const updateItem = (index: number, field: 'product_id' | 'quantity', value: string | number) => {
    const nextItems = [...items]
    nextItems[index] = { ...nextItems[index], [field]: field === 'quantity' ? Number(value) : value }
    setItems(nextItems)
  }

  const addItem = () => setItems([...items, { product_id: '', quantity: 1 }])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    try {
      const response = await dispatchService.create({
        order_id: orderId,
        tracking_number: trackingNumber || null,
        courier_name: courierName || null,
        notes: notes || null,
        items: items.map((item) => ({ product_id: item.product_id, quantity: item.quantity })),
      })
      if (response.success) {
        navigate(`/dispatch/${response.data?.id}`)
      } else {
        setError(response.message || 'Failed to create dispatch')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create dispatch')
    }
  }

  return (
    <div className="mx-auto max-w-3xl rounded-lg border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-surface-dark">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Create Dispatch</h2>
          <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">Create a new dispatch for an approved order.</p>
        </div>
        <button type="button" onClick={() => navigate('/dispatch')} className="text-sm font-medium text-primary-600 hover:text-primary-700">
          Back to list
        </button>
      </div>

      <form className="mt-6 space-y-6" onSubmit={handleSubmit}>
        {error ? <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

        <div className="grid gap-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900/60 md:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Order ID</label>
            <input value={orderId} onChange={(event) => setOrderId(event.target.value)} required className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Courier</label>
            <input value={courierName} onChange={(event) => setCourierName(event.target.value)} className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
          </div>
        </div>

        <div className="grid gap-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900/60 md:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Tracking Number</label>
            <input value={trackingNumber} onChange={(event) => setTrackingNumber(event.target.value)} className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Notes</label>
            <input value={notes} onChange={(event) => setNotes(event.target.value)} className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
          </div>
        </div>

        <div className="space-y-3 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-neutral-900/60">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">Items</h3>
            <button type="button" onClick={addItem} className="inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700">
              <Plus className="h-4 w-4" />
              Add Item
            </button>
          </div>
          {items.map((item, index) => (
            <div key={index} className="grid gap-4 rounded-lg border border-neutral-200 p-4 dark:border-neutral-800 md:grid-cols-[1fr_120px]">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Product ID</label>
                <input value={item.product_id} onChange={(event) => updateItem(index, 'product_id', event.target.value)} required className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Quantity</label>
                <input type="number" min="1" value={item.quantity} onChange={(event) => updateItem(index, 'quantity', event.target.value)} className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-end">
          <button type="submit" className="h-10 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700">
            Create Dispatch
          </button>
        </div>
      </form>
    </div>
  )
}
