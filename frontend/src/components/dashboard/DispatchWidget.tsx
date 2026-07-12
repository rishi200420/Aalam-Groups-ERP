import { AlertTriangle, CheckCircle2, Clock, Truck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { dispatchService } from '@/services/dispatch.service'
import type { DashboardDispatch } from '@/types'

interface DispatchWidgetProps {
  dispatch?: DashboardDispatch
  isLoading?: boolean
}

interface DispatchSummary {
  pending: number
  delivered_today: number
  in_transit: number
  failed: number
}

export function DispatchWidget({ isLoading }: DispatchWidgetProps) {
  const navigate = useNavigate()
  const [summary, setSummary] = useState<DispatchSummary>({ pending: 0, delivered_today: 0, in_transit: 0, failed: 0 })
  const [loading, setLoading] = useState(true)

  const loadSummary = async () => {
    try {
      setLoading(true)
      const response = await dispatchService.list()
      const dispatches = response.data ?? []
      const today = new Date().toISOString().slice(0, 10)
      const nextSummary = dispatches.reduce<DispatchSummary>(
        (acc, item) => {
          if (item.status === 'ready' || item.status === 'dispatched') acc.pending += 1
          if (item.status === 'in_transit') acc.in_transit += 1
          if (item.status === 'failed') acc.failed += 1
          if (item.status === 'delivered' && item.updated_at.slice(0, 10) === today) acc.delivered_today += 1
          return acc
        },
        { pending: 0, delivered_today: 0, in_transit: 0, failed: 0 }
      )
      setSummary(nextSummary)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadSummary()
    const handleRefresh = () => {
      void loadSummary()
    }
    window.addEventListener('dispatch-status-updated', handleRefresh)
    return () => window.removeEventListener('dispatch-status-updated', handleRefresh)
  }, [])

  const rows = [
    { label: 'Pending Dispatch', value: summary.pending, icon: Clock, color: 'text-amber-600' },
    { label: 'Delivered Today', value: summary.delivered_today, icon: CheckCircle2, color: 'text-green-600' },
    { label: 'In Transit', value: summary.in_transit, icon: Truck, color: 'text-sky-600' },
    { label: 'Failed Deliveries', value: summary.failed, icon: AlertTriangle, color: 'text-red-600' },
  ]

  return (
    <div className="h-full rounded-xl border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
      <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Dispatch Overview</h3>
      <div className="mt-4 space-y-2">
        {rows.map((row) => (
          <button
            key={row.label}
            type="button"
            onClick={() => navigate('/dispatch')}
            className="flex w-full items-center justify-between rounded-lg border border-neutral-100 px-3 py-2.5 text-left hover:bg-neutral-50 dark:border-neutral-800 dark:hover:bg-neutral-800"
          >
            <span className="flex items-center gap-2 text-sm text-neutral-700 dark:text-neutral-300">
              <row.icon className={`h-4 w-4 ${row.color}`} />
              {row.label}
            </span>
            {(isLoading || loading) ? (
              <span className="h-5 w-6 animate-pulse rounded bg-neutral-200 dark:bg-neutral-700" />
            ) : (
              <span className="text-sm font-semibold text-neutral-900 dark:text-neutral-50">{row.value}</span>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}
