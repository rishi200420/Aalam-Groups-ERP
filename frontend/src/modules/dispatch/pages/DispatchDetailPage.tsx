import { ArrowLeft } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { dispatchService } from '@/services/dispatch.service'
import type { Dispatch, DispatchStatus } from '@/types'
import { DispatchStatusBadge } from '../components/DispatchStatusBadge'
import { DispatchTimeline } from '../components/DispatchTimeline'

// Mirrors the backend's DISPATCH_TRANSITIONS map so the UI only ever offers a
// status change that the server will actually accept.
const DISPATCH_TRANSITIONS: Record<DispatchStatus, DispatchStatus[]> = {
  ready: ['dispatched', 'failed', 'returned'],
  dispatched: ['in_transit', 'failed', 'returned'],
  in_transit: ['delivered', 'failed', 'returned'],
  delivered: [],
  failed: [],
  returned: [],
}

const STATUS_LABELS: Record<DispatchStatus, string> = {
  ready: 'Ready',
  dispatched: 'Dispatched',
  in_transit: 'In Transit',
  delivered: 'Delivered',
  failed: 'Failed',
  returned: 'Returned',
}

export function DispatchDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [dispatch, setDispatch] = useState<Dispatch | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [status, setStatus] = useState<DispatchStatus | ''>('')
  const [notes, setNotes] = useState('')

  const loadDispatch = async () => {
    if (!id) return
    try {
      setLoading(true)
      setLoadError(null)
      const response = await dispatchService.get(id)
      if (response.success) {
        const nextOptions = response.data ? DISPATCH_TRANSITIONS[response.data.status] : []
        setDispatch(response.data || null)
        setStatus(nextOptions && nextOptions.length > 0 ? nextOptions[0] : '')
      } else {
        setLoadError(response.message || 'Failed to load dispatch')
      }
    } catch (err) {
      setLoadError(err instanceof Error ? err.message : 'Failed to load dispatch')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadDispatch()
  }, [id])

  const availableStatuses = dispatch ? DISPATCH_TRANSITIONS[dispatch.status] : []

  const handleStatusUpdate = async () => {
    if (!dispatch || !status) return
    setActionError(null)
    try {
      const response = await dispatchService.updateStatus(dispatch.id, { status, notes: notes || null })
      if (response.success) {
        setDispatch(response.data || null)
        const nextOptions = response.data ? DISPATCH_TRANSITIONS[response.data.status] : []
        setStatus(nextOptions && nextOptions.length > 0 ? nextOptions[0] : '')
        setNotes('')
        window.dispatchEvent(new Event('dispatch-status-updated'))
      } else {
        setActionError(response.message || 'Failed to update status')
      }
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Failed to update status')
    }
  }

  if (loading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-10 text-center text-sm text-neutral-600 dark:border-neutral-800 dark:bg-surface-dark dark:text-neutral-400">Loading dispatch...</div>
  }

  if (loadError || !dispatch) {
    return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-700">{loadError || 'Dispatch not found'}</div>
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-3">
            <button type="button" onClick={() => navigate('/dispatch')} className="inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700">
              <ArrowLeft className="h-4 w-4" />
              Back to dispatches
            </button>
            <DispatchStatusBadge status={dispatch.status} />
          </div>
          <h2 className="mt-2 text-2xl font-semibold text-neutral-900 dark:text-neutral-50">{dispatch.dispatch_number}</h2>
          <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">Order {dispatch.order_number || dispatch.order_id}</p>
        </div>
        <Link to="/dispatch" className="inline-flex h-10 items-center justify-center rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300 dark:hover:bg-neutral-800">
          Manage Dispatches
        </Link>
      </div>

      <div className="grid gap-5 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-5">
          <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">Dispatch Summary</h3>
            <dl className="mt-4 grid gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm text-neutral-500">Tracking Number</dt>
                <dd className="mt-1 text-sm font-medium text-neutral-900 dark:text-neutral-50">{dispatch.tracking_number || '—'}</dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-500">Courier</dt>
                <dd className="mt-1 text-sm font-medium text-neutral-900 dark:text-neutral-50">{dispatch.courier_name || '—'}</dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-500">Created</dt>
                <dd className="mt-1 text-sm font-medium text-neutral-900 dark:text-neutral-50">{new Date(dispatch.created_at).toLocaleString()}</dd>
              </div>
              <div>
                <dt className="text-sm text-neutral-500">Updated</dt>
                <dd className="mt-1 text-sm font-medium text-neutral-900 dark:text-neutral-50">{new Date(dispatch.updated_at).toLocaleString()}</dd>
              </div>
            </dl>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">Items</h3>
            <div className="mt-4 space-y-3">
              {dispatch.items.map((item) => (
                <div key={item.id} className="flex items-center justify-between rounded-lg border border-neutral-200 p-3 dark:border-neutral-800">
                  <div>
                    <p className="text-sm font-medium text-neutral-900 dark:text-neutral-50">{item.product?.name || item.product_id}</p>
                    <p className="text-sm text-neutral-500">Qty {item.quantity}</p>
                  </div>
                  <p className="text-sm font-medium text-neutral-900 dark:text-neutral-50">{item.line_total}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">Timeline</h3>
            <div className="mt-4">
              <DispatchTimeline entries={dispatch.timelines} />
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">Update Status</h3>
          {actionError && <div className="mt-3 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{actionError}</div>}
          {availableStatuses.length === 0 ? (
            <p className="mt-4 text-sm text-neutral-500">This dispatch is {STATUS_LABELS[dispatch.status]} and can no longer be updated.</p>
          ) : (
            <div className="mt-4 space-y-4">
              <div>
                <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Status</label>
                <select
                  value={status}
                  onChange={(event) => setStatus(event.target.value as DispatchStatus)}
                  className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
                >
                  {availableStatuses.map((option) => (
                    <option key={option} value={option}>{STATUS_LABELS[option]}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="mb-1.5 block text-sm font-medium text-neutral-700 dark:text-neutral-300">Notes</label>
                <textarea
                  value={notes}
                  onChange={(event) => setNotes(event.target.value)}
                  rows={4}
                  className="w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
                  placeholder="Add a note for this status change"
                />
              </div>
              <button type="button" onClick={() => void handleStatusUpdate()} disabled={!status} className="h-10 w-full rounded-lg bg-primary-600 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60">
                Save Status
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
