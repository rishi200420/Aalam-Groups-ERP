import { Printer } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { orderService } from '@/services/order.service'
import type { Order } from '@/types'

const statusStyles: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-800',
  approved: 'bg-blue-100 text-blue-800',
  packed: 'bg-indigo-100 text-indigo-800',
  dispatched: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

export function OrderDetailPage() {
  const { id } = useParams()
  const [order, setOrder] = useState<Order | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    void orderService.get(id).then((response) => setOrder(response.data ?? null)).finally(() => setIsLoading(false))
  }, [id])

  if (isLoading) return <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm">Loading order...</div>
  if (!order) return <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm">Order not found.</div>

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between print:hidden">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Order {order.order_number}</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">{order.outlet_name} · {new Date(order.created_at).toLocaleString()}</p>
        </div>
        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center rounded px-3 py-1.5 text-sm font-medium capitalize ${statusStyles[order.status]}`}>{order.status}</span>
          <button type="button" onClick={() => window.print()} className="inline-flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-medium hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
            <Printer className="h-4 w-4" /> Print Invoice
          </button>
        </div>
      </div>

      <div className="rounded-lg border border-neutral-200 bg-white p-6 dark:border-neutral-800 dark:bg-surface-dark print:border-none">
        <div className="mb-6 flex items-start justify-between">
          <div>
            <p className="text-lg font-bold text-neutral-900 dark:text-neutral-50">Aalam Groups</p>
            <p className="text-sm text-neutral-500">TASTIQ &amp; LEMURIA</p>
          </div>
          <div className="text-right text-sm text-neutral-600 dark:text-neutral-400">
            <p>Order: {order.order_number}</p>
            <p>Date: {new Date(order.created_at).toLocaleDateString()}</p>
            <p>Bill to: {order.outlet_name}</p>
          </div>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-neutral-200 text-left text-xs uppercase tracking-wide text-neutral-500 dark:border-neutral-800">
              <th className="py-2">Product</th>
              <th className="py-2 text-right">Qty</th>
              <th className="py-2 text-right">Unit Price</th>
              <th className="py-2 text-right">Total</th>
            </tr>
          </thead>
          <tbody>
            {order.items.map((item) => (
              <tr key={item.id} className="border-b border-neutral-100 dark:border-neutral-800">
                <td className="py-2">{item.product?.name ?? item.product_id}</td>
                <td className="py-2 text-right">{item.quantity}</td>
                <td className="py-2 text-right">₹{item.unit_price}</td>
                <td className="py-2 text-right">₹{item.line_total}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="mt-4 flex justify-end">
          <div className="w-56 space-y-1 text-sm">
            <div className="flex justify-between"><span className="text-neutral-500">Subtotal</span><span>₹{order.subtotal}</span></div>
            <div className="flex justify-between border-t border-neutral-200 pt-1 font-semibold text-neutral-900 dark:border-neutral-800 dark:text-neutral-50">
              <span>Total</span><span>₹{order.total_amount}</span>
            </div>
          </div>
        </div>

        {order.notes && (
          <div className="mt-4 rounded-lg bg-neutral-50 p-3 text-sm text-neutral-600 dark:bg-neutral-900 dark:text-neutral-400">
            Notes: {order.notes}
          </div>
        )}
      </div>

      <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark print:hidden">
        <h3 className="mb-3 font-semibold text-neutral-900 dark:text-neutral-50">Order Timeline</h3>
        <ol className="space-y-3 border-l border-neutral-200 pl-4 dark:border-neutral-800">
          {order.status_history.map((entry) => (
            <li key={entry.id} className="relative">
              <span className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-primary-600" />
              <p className="text-sm font-medium capitalize text-neutral-900 dark:text-neutral-50">{entry.status}</p>
              {entry.notes && <p className="text-xs text-neutral-500">{entry.notes}</p>}
              <p className="text-xs text-neutral-400">{new Date(entry.changed_at).toLocaleString()}</p>
            </li>
          ))}
        </ol>
      </div>
    </div>
  )
}
