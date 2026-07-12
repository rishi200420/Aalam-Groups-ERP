import { Link } from 'react-router-dom'
import type { DashboardRecentOrder } from '@/types'

const statusStyles: Record<string, string> = {
  pending: 'bg-amber-100 text-amber-800',
  approved: 'bg-blue-100 text-blue-800',
  packed: 'bg-indigo-100 text-indigo-800',
  dispatched: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

interface RecentOrdersProps {
  orders: DashboardRecentOrder[]
  isLoading?: boolean
}

export function RecentOrders({ orders, isLoading }: RecentOrdersProps) {
  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-surface-dark p-5 h-full">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Recent Orders</h3>
        <Link to="/orders" className="text-sm font-medium text-primary-600 hover:text-primary-700">View all</Link>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[...Array(4)].map((_, index) => (
            <div key={index} className="h-12 animate-pulse rounded-lg bg-neutral-100 dark:bg-neutral-800" />
          ))}
        </div>
      ) : orders.length === 0 ? (
        <p className="py-6 text-center text-sm text-neutral-500">No orders yet. Orders will appear here as they're placed.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-200 text-left text-xs uppercase tracking-wide text-neutral-500 dark:border-neutral-800">
                <th className="py-2 pr-3">Order</th>
                <th className="py-2 pr-3">Outlet</th>
                <th className="py-2 pr-3 hidden lg:table-cell">Distributor</th>
                <th className="py-2 pr-3 hidden md:table-cell">Brand</th>
                <th className="py-2 pr-3 hidden xl:table-cell">Products</th>
                <th className="py-2 pr-3 text-right">Amount</th>
                <th className="py-2 pr-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id} className="border-b border-neutral-100 last:border-0 dark:border-neutral-800/60">
                  <td className="py-2.5 pr-3">
                    <Link to={`/orders/${order.id}`} className="font-medium text-neutral-900 hover:text-primary-600 dark:text-neutral-50">
                      {order.order_number}
                    </Link>
                    <p className="text-xs text-neutral-400">{new Date(order.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                  </td>
                  <td className="py-2.5 pr-3 text-neutral-700 dark:text-neutral-300">{order.outlet_name}</td>
                  <td className="py-2.5 pr-3 hidden lg:table-cell text-neutral-700 dark:text-neutral-300">{order.distributor_name ?? '—'}</td>
                  <td className="py-2.5 pr-3 hidden md:table-cell text-neutral-700 dark:text-neutral-300">{order.brands.join(', ') || '—'}</td>
                  <td className="py-2.5 pr-3 hidden xl:table-cell text-neutral-500">{order.product_summary}</td>
                  <td className="py-2.5 pr-3 text-right font-medium text-neutral-900 dark:text-neutral-50">₹{order.total_amount}</td>
                  <td className="py-2.5 pr-3">
                    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-medium capitalize ${statusStyles[order.status]}`}>
                      {order.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
