import { AlertTriangle, BarChart3, Boxes, ShoppingCart, Store, Truck, Users, Wallet } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { StatsCard } from '@/components/dashboard/StatsCard'
import type { DashboardStats as DashboardStatsType } from '@/types'

interface DashboardStatsProps {
  stats: DashboardStatsType | null
  isLoading: boolean
}

export function DashboardStats({ stats, isLoading }: DashboardStatsProps) {
  const navigate = useNavigate()
  const money = (value: string | undefined) => `₹${Number(value ?? 0).toLocaleString('en-IN')}`

  const cards = [
    { label: 'Orders Today', value: String(stats?.orders_today ?? 0), icon: ShoppingCart, onClick: () => navigate('/orders') },
    { label: 'Revenue Today', value: money(stats?.revenue_today), icon: Wallet },
    { label: 'Revenue (MTD)', value: money(stats?.revenue_mtd), icon: BarChart3 },
    { label: 'Pending Dispatch', value: String(stats?.pending_dispatch ?? 0), icon: Truck, onClick: () => navigate('/orders?status=approved') },
    { label: 'Active Outlets', value: `${stats?.active_outlets ?? 0} / ${stats?.total_outlets ?? 0}`, icon: Store, onClick: () => navigate('/outlets') },
    { label: 'Total Products', value: String(stats?.total_products ?? 0), icon: Boxes, onClick: () => navigate('/products') },
    { label: 'Total Distributors', value: String(stats?.total_distributors ?? 0), icon: Users, onClick: () => navigate('/users') },
    {
      label: 'Low Stock Alerts',
      value: String(stats?.low_stock_products ?? 0),
      icon: AlertTriangle,
      trend: stats?.out_of_stock_products ? `${stats.out_of_stock_products} out of stock` : undefined,
      onClick: () => navigate('/products?low_stock_only=true'),
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      {cards.map((card) => (
        <StatsCard key={card.label} {...card} isLoading={isLoading} />
      ))}
    </div>
  )
}
