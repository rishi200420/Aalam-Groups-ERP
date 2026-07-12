import { Download, PlusCircle, ShoppingCart, Store } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import type { DashboardRecentOrder } from '@/types'

interface QuickActionsProps {
  recentOrders: DashboardRecentOrder[]
}

function exportOrdersCsv(orders: DashboardRecentOrder[]) {
  const headers = ['Order Number', 'Outlet', 'Distributor', 'Brands', 'Products', 'Amount', 'Status', 'Created At']
  const rows = orders.map((order) => [
    order.order_number,
    order.outlet_name,
    order.distributor_name ?? '',
    order.brands.join(' / '),
    order.product_summary,
    order.total_amount,
    order.status,
    new Date(order.created_at).toLocaleString(),
  ])
  const csv = [headers, ...rows]
    .map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `aalam-orders-report-${new Date().toISOString().slice(0, 10)}.csv`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

export function QuickActions({ recentOrders }: QuickActionsProps) {
  const navigate = useNavigate()

  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-surface-dark p-5 h-full">
      <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Quick Actions</h3>
      <div className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-3 xl:grid-cols-1">
        <button
          type="button"
          onClick={() => navigate('/outlets/new')}
          className="flex w-full items-center justify-center gap-2 h-10 rounded-lg bg-primary-600 text-white text-sm font-medium hover:bg-primary-700"
        >
          <Store className="h-4 w-4" />
          Add Outlet
        </button>
        <button
          type="button"
          onClick={() => navigate('/orders/new')}
          className="flex w-full items-center justify-center gap-2 h-10 rounded-lg border border-neutral-200 dark:border-neutral-700 text-sm font-medium hover:bg-neutral-50 dark:hover:bg-neutral-800"
        >
          <ShoppingCart className="h-4 w-4" />
          Create Order
        </button>
        <button
          type="button"
          onClick={() => navigate('/products/new')}
          className="flex w-full items-center justify-center gap-2 h-10 rounded-lg border border-neutral-200 dark:border-neutral-700 text-sm font-medium hover:bg-neutral-50 dark:hover:bg-neutral-800"
        >
          <PlusCircle className="h-4 w-4" />
          Add Product
        </button>
        <button
          type="button"
          onClick={() => exportOrdersCsv(recentOrders)}
          disabled={recentOrders.length === 0}
          className="flex w-full items-center justify-center gap-2 h-10 rounded-lg bg-gold-500 text-neutral-900 text-sm font-medium hover:bg-gold-500/90 disabled:opacity-50 sm:col-span-3 xl:col-span-1"
        >
          <Download className="h-4 w-4" />
          Export Report (CSV)
        </button>
      </div>
    </div>
  )
}
