import { AlertCircle, RefreshCw } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuth } from '@/app/providers/AuthProvider'
import { useBrandFilter } from '@/app/providers/BrandFilterProvider'
import { ActivityFeed } from '@/components/dashboard/ActivityFeed'
import { DashboardStats } from '@/components/dashboard/DashboardStats'
import { DispatchWidget } from '@/components/dashboard/DispatchWidget'
import { QuickActions } from '@/components/dashboard/QuickActions'
import { RecentOrders } from '@/components/dashboard/RecentOrders'
import { RevenueChart } from '@/components/dashboard/RevenueChart'
import { dashboardService } from '@/services/dashboard.service'
import type { DashboardStats as DashboardStatsType } from '@/types'

const REFRESH_INTERVAL_MS = 30_000

export function FounderDashboardPage() {
  const { user } = useAuth()
  const { brand } = useBrandFilter()
  const [stats, setStats] = useState<DashboardStatsType | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const load = useCallback(
    async (showSpinner: boolean) => {
      if (showSpinner) setIsLoading(true)
      setError(null)
      try {
        const response = await dashboardService.getStats(brand)
        setStats(response.data ?? null)
      } catch {
        setError('Unable to load dashboard')
      } finally {
        if (showSpinner) setIsLoading(false)
      }
    },
    [brand]
  )

  useEffect(() => {
    void load(true)

    if (intervalRef.current) clearInterval(intervalRef.current)
    intervalRef.current = setInterval(() => {
      void load(false)
    }, REFRESH_INTERVAL_MS)

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [load])

  if (error && !stats) {
    return (
      <div className="flex flex-col items-center justify-center gap-3 rounded-xl border border-neutral-200 bg-white p-10 text-center dark:border-neutral-800 dark:bg-surface-dark">
        <AlertCircle className="h-8 w-8 text-red-500" />
        <p className="font-medium text-neutral-900 dark:text-neutral-50">{error}</p>
        <button
          type="button"
          onClick={() => void load(true)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        >
          <RefreshCw className="h-4 w-4" /> Retry
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">
            Welcome back, {user?.full_name?.split(' ')[0] ?? 'Founder'}
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            Executive overview across TASTIQ, LEMURIA, and all territories.
            {brand !== 'all' && <span className="ml-1 font-medium text-primary-600">Filtered: {brand.toUpperCase()}</span>}
          </p>
        </div>
        {error && stats && (
          <p className="flex items-center gap-1.5 text-xs text-amber-600">
            <AlertCircle className="h-3.5 w-3.5" /> Showing last known data — refresh failed
          </p>
        )}
      </div>

      <DashboardStats stats={stats} isLoading={isLoading} />

      <RevenueChart
        ordersLast7Days={stats?.orders_last_7_days ?? []}
        revenueLast30Days={stats?.revenue_last_30_days ?? []}
        isLoading={isLoading}
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className="xl:col-span-2">
          <RecentOrders orders={stats?.recent_orders ?? []} isLoading={isLoading} />
        </div>
        <QuickActions recentOrders={stats?.recent_orders ?? []} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <DispatchWidget dispatch={stats?.dispatch ?? { pending: 0, completed_today: 0, delayed: 0 }} isLoading={isLoading} />
        <ActivityFeed activities={stats?.recent_activities ?? []} isLoading={isLoading} />
      </div>
    </div>
  )
}
