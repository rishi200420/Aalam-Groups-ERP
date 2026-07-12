import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { DashboardDailyCount, DashboardDailyRevenue } from '@/types'

interface RevenueChartProps {
  ordersLast7Days: DashboardDailyCount[]
  revenueLast30Days: DashboardDailyRevenue[]
  isLoading?: boolean
}

function formatShortDate(value: string) {
  return new Date(value).toLocaleDateString(undefined, { day: '2-digit', month: 'short' })
}

export function RevenueChart({ ordersLast7Days, revenueLast30Days, isLoading }: RevenueChartProps) {
  const orderData = ordersLast7Days.map((point) => ({ date: formatShortDate(point.date), count: point.count }))
  const revenueData = revenueLast30Days.map((point) => ({ date: formatShortDate(point.date), revenue: Number(point.revenue) }))

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div className="h-64 animate-pulse rounded-xl border border-neutral-200 bg-neutral-100 dark:border-neutral-800 dark:bg-neutral-800" />
        <div className="h-64 animate-pulse rounded-xl border border-neutral-200 bg-neutral-100 dark:border-neutral-800 dark:bg-neutral-800" />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
      <div className="rounded-xl border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <h3 className="mb-4 font-semibold text-neutral-900 dark:text-neutral-50">Orders — Last 7 Days</h3>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={orderData}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-neutral-200 dark:stroke-neutral-800" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="currentColor" className="text-neutral-500" />
            <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke="currentColor" className="text-neutral-500" />
            <Tooltip contentStyle={{ borderRadius: 8, fontSize: 13 }} />
            <Bar dataKey="count" name="Orders" fill="#c9a24b" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="rounded-xl border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <h3 className="mb-4 font-semibold text-neutral-900 dark:text-neutral-50">Revenue — Last 30 Days</h3>
        <ResponsiveContainer width="100%" height={220}>
          <AreaChart data={revenueData}>
            <defs>
              <linearGradient id="revenueFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#7c3aed" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#7c3aed" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" className="stroke-neutral-200 dark:stroke-neutral-800" />
            <XAxis dataKey="date" tick={{ fontSize: 11 }} interval={4} stroke="currentColor" className="text-neutral-500" />
            <YAxis tick={{ fontSize: 12 }} stroke="currentColor" className="text-neutral-500" />
            <Tooltip contentStyle={{ borderRadius: 8, fontSize: 13 }} formatter={(value) => [`₹${Number(value ?? 0).toLocaleString()}`, 'Revenue']} />
            <Area type="monotone" dataKey="revenue" stroke="#7c3aed" fill="url(#revenueFill)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
