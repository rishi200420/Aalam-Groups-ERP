import { Download, Plus, Search } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { dispatchService } from '@/services/dispatch.service'
import type { Dispatch, DispatchStatus } from '@/types'
import { DispatchStatusBadge } from '../components/DispatchStatusBadge'

const PAGE_SIZE = 10

export function DispatchListPage() {
  const [dispatches, setDispatches] = useState<Dispatch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState<DispatchStatus | ''>('')
  const [page, setPage] = useState(1)

  const loadDispatches = async () => {
    try {
      setLoading(true)
      const response = await dispatchService.list({
        search: search || undefined,
        status: status || undefined,
      })
      if (response.success) {
        setDispatches(response.data || [])
      } else {
        setError(response.message || 'Failed to load dispatches')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dispatches')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadDispatches()
  }, [search, status])

  const filteredDispatches = useMemo(() => {
    const term = search.toLowerCase()
    return dispatches.filter((dispatch) => {
      const searchText = [dispatch.dispatch_number, dispatch.order_number, dispatch.tracking_number].filter(Boolean).join(' ').toLowerCase()
      const matchesSearch = !term || searchText.includes(term)
      const matchesStatus = !status || dispatch.status === status
      return matchesSearch && matchesStatus
    })
  }, [dispatches, search, status])

  const pagedDispatches = useMemo(() => {
    const start = (page - 1) * PAGE_SIZE
    return filteredDispatches.slice(start, start + PAGE_SIZE)
  }, [filteredDispatches, page])

  const totalPages = Math.max(1, Math.ceil(filteredDispatches.length / PAGE_SIZE))

  useEffect(() => {
    setPage(1)
  }, [search, status])

  const handleExport = () => {
    const rows = filteredDispatches.map((dispatch) => [
      dispatch.dispatch_number,
      dispatch.order_number || '',
      dispatch.status,
      dispatch.tracking_number || '',
      dispatch.courier_name || '',
      new Date(dispatch.created_at).toLocaleDateString(),
    ])

    const csv = [['Dispatch Number', 'Order Number', 'Status', 'Tracking Number', 'Courier', 'Created At'], ...rows]
      .map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'dispatches.csv'
    link.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Dispatches</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Track and manage shipment dispatches end-to-end.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={handleExport}
            className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-800"
          >
            <Download className="h-4 w-4" />
            Export CSV
          </button>
          <Link to="/dispatch/create" className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700">
            <Plus className="h-4 w-4" />
            Create Dispatch
          </Link>
        </div>
      </div>

      <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark sm:grid-cols-[1fr_200px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          <input
            value={search}
            onChange={(event) => {
              setSearch(event.target.value)
              setPage(1)
            }}
            placeholder="Search dispatch number or order"
            className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-10 pr-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
        </div>
        <select
          value={status}
          onChange={(event) => {
            setStatus(event.target.value as DispatchStatus | '')
            setPage(1)
          }}
          className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        >
          <option value="">All Status</option>
          <option value="ready">Ready</option>
          <option value="dispatched">Dispatched</option>
          <option value="in_transit">In Transit</option>
          <option value="delivered">Delivered</option>
          <option value="failed">Failed</option>
          <option value="returned">Returned</option>
        </select>
      </div>

      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        <div className="hidden grid-cols-[1fr_1fr_1fr_1fr_140px] gap-4 border-b border-neutral-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-neutral-500 md:grid dark:border-neutral-800">
          <span>Dispatch</span>
          <span>Order</span>
          <span>Status</span>
          <span>Tracking</span>
          <span>Action</span>
        </div>
        {loading ? (
          <div className="p-6 text-sm text-neutral-600 dark:text-neutral-400">Loading dispatches...</div>
        ) : error ? (
          <div className="p-6 text-sm text-red-600">{error}</div>
        ) : filteredDispatches.length === 0 ? (
          <div className="p-6 text-sm text-neutral-600 dark:text-neutral-400">No dispatches found.</div>
        ) : (
          pagedDispatches.map((dispatch) => (
            <div key={dispatch.id} className="grid gap-3 border-b border-neutral-100 px-4 py-4 last:border-0 md:grid-cols-[1fr_1fr_1fr_1fr_140px] md:items-center dark:border-neutral-800/60">
              <div>
                <Link to={`/dispatch/${dispatch.id}`} className="font-semibold text-neutral-900 hover:text-primary-600 dark:text-neutral-50">
                  {dispatch.dispatch_number}
                </Link>
                <p className="text-xs text-neutral-500">{new Date(dispatch.created_at).toLocaleDateString()}</p>
              </div>
              <span className="text-sm text-neutral-700 dark:text-neutral-300">{dispatch.order_number || '—'}</span>
              <DispatchStatusBadge status={dispatch.status} />
              <span className="text-sm text-neutral-700 dark:text-neutral-300">{dispatch.tracking_number || '—'}</span>
              <Link to={`/dispatch/${dispatch.id}`} className="text-sm font-medium text-primary-600 hover:text-primary-700">
                View
              </Link>
            </div>
          ))
        )}
      </div>

      {!loading && !error && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-neutral-500">Page {page} of {Math.max(totalPages, 1)}</p>
          <div className="flex gap-2">
            <button type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Previous</button>
            <button type="button" disabled={totalPages === 0 || page >= totalPages} onClick={() => setPage((value) => value + 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Next</button>
          </div>
        </div>
      )}
    </div>
  )
}
