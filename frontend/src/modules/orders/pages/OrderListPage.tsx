import { CheckCircle2, PackageCheck, Plus, Search, Truck, XCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { orderService } from '@/services/order.service'
import type { Order, OrderStatus } from '@/types'

const statusStyles: Record<OrderStatus, string> = {
  pending: 'bg-amber-100 text-amber-800',
  approved: 'bg-blue-100 text-blue-800',
  packed: 'bg-indigo-100 text-indigo-800',
  dispatched: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const nextStatusAction: Partial<Record<OrderStatus, { label: string; next: OrderStatus; icon: typeof PackageCheck }>> = {
  approved: { label: 'Mark Packed', next: 'packed', icon: PackageCheck },
  packed: { label: 'Mark Dispatched', next: 'dispatched', icon: Truck },
  dispatched: { label: 'Mark Delivered', next: 'delivered', icon: CheckCircle2 },
}

export function OrderListPage() {
  const { isFounder } = useAuth()
  const [searchParams] = useSearchParams()
  const [orders, setOrders] = useState<Order[]>([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState(searchParams.get('status') ?? '')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  const load = () => {
    setIsLoading(true)
    void orderService
      .list({ page, page_size: 10, search: search || undefined, status: status || undefined })
      .then((response) => {
        setOrders(response.data ?? [])
        setTotalPages(response.total_pages)
      })
      .finally(() => setIsLoading(false))
  }

  useEffect(load, [page, search, status])

  const approve = async (order: Order) => {
    await orderService.approve(order.id)
    load()
  }

  const reject = async (order: Order) => {
    const reason = window.prompt('Reason for rejecting this order?', 'Rejected by founder')
    if (reason === null) return
    await orderService.reject(order.id, reason)
    load()
  }

  const advance = async (order: Order, next: OrderStatus) => {
    await orderService.advanceStatus(order.id, next)
    load()
  }

  const cancel = async (order: Order) => {
    const reason = window.prompt('Reason for cancelling this order?', 'Cancelled')
    if (reason === null) return
    await orderService.cancel(order.id, reason)
    load()
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Orders</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Track and manage outlet orders end-to-end.</p>
        </div>
        <Link to="/orders/new" className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700">
          <Plus className="h-4 w-4" />
          Create Order
        </Link>
      </div>

      <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark sm:grid-cols-[1fr_200px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          <input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} placeholder="Search order number" className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-10 pr-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
        </div>
        <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1) }} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
          <option value="">All Status</option>
          {Object.keys(statusStyles).map((value) => <option key={value} value={value}>{value}</option>)}
        </select>
      </div>

      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        <div className="hidden grid-cols-[1fr_1fr_1fr_1fr_1fr_180px] gap-4 border-b border-neutral-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-neutral-500 md:grid">
          <span>Order</span>
          <span>Outlet</span>
          <span>Distributor</span>
          <span>Amount</span>
          <span>Status</span>
          <span>Actions</span>
        </div>
        {isLoading ? (
          <div className="p-6 text-sm text-neutral-600">Loading orders...</div>
        ) : orders.length === 0 ? (
          <div className="p-6 text-sm text-neutral-600">No orders found.</div>
        ) : (
          orders.map((order) => {
            const advanceAction = nextStatusAction[order.status]
            return (
              <div key={order.id} className="grid gap-3 border-b border-neutral-100 px-4 py-4 last:border-0 md:grid-cols-[1fr_1fr_1fr_1fr_1fr_180px] md:items-center">
                <div>
                  <Link to={`/orders/${order.id}`} className="font-semibold text-neutral-900 hover:text-primary-600 dark:text-neutral-50">
                    {order.order_number}
                  </Link>
                  <p className="text-xs text-neutral-500">{new Date(order.created_at).toLocaleDateString()}</p>
                </div>
                <span className="text-sm text-neutral-700 dark:text-neutral-300">{order.outlet_name}</span>
                <span className="text-sm text-neutral-700 dark:text-neutral-300">{order.distributor_name ?? 'Unassigned'}</span>
                <span className="text-sm font-medium text-neutral-900 dark:text-neutral-50">₹{order.total_amount}</span>
                <span className={`inline-flex w-fit items-center rounded px-2 py-1 text-xs font-medium capitalize ${statusStyles[order.status]}`}>{order.status}</span>
                <div className="flex flex-wrap items-center gap-2">
                  {isFounder && order.status === 'pending' && (
                    <>
                      <button type="button" title="Approve" onClick={() => void approve(order)} className="rounded-lg border border-green-200 p-2 text-green-700 hover:bg-green-50">
                        <CheckCircle2 className="h-4 w-4" />
                      </button>
                      <button type="button" title="Reject" onClick={() => void reject(order)} className="rounded-lg border border-red-200 p-2 text-red-600 hover:bg-red-50">
                        <XCircle className="h-4 w-4" />
                      </button>
                    </>
                  )}
                  {advanceAction && (
                    <button type="button" title={advanceAction.label} onClick={() => void advance(order, advanceAction.next)} className="rounded-lg border border-neutral-200 p-2 hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
                      <advanceAction.icon className="h-4 w-4" />
                    </button>
                  )}
                  {!['delivered', 'cancelled'].includes(order.status) && (
                    <button type="button" title="Cancel" onClick={() => void cancel(order)} className="rounded-lg border border-neutral-200 p-2 text-neutral-500 hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
                      <XCircle className="h-4 w-4" />
                    </button>
                  )}
                </div>
              </div>
            )
          })
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
