import { AlertTriangle, Bell, Check, CheckCheck, Package, ShoppingCart, Trash2, Truck } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { notificationService } from '@/services/notification.service'
import type { Notification } from '@/types'

const TYPE_ICON: Record<string, typeof Bell> = {
  order_created: ShoppingCart,
  order_approved: ShoppingCart,
  order_cancelled: ShoppingCart,
  order_rejected: ShoppingCart,
  order_delivered: Package,
  dispatch_created: Truck,
  dispatch_delivered: Truck,
  dispatch_failed: Truck,
  low_stock: AlertTriangle,
  out_of_stock: AlertTriangle,
}

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diffMs / 60000)
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

export function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadOnly, setUnreadOnly] = useState(false)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await notificationService.list({ page, page_size: 20, unread_only: unreadOnly })
      setNotifications(response.data ?? [])
      setTotalPages(response.total_pages)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load notifications')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, unreadOnly])

  const handleMarkRead = async (id: string) => {
    await notificationService.markRead(id)
    setNotifications((current) => current.map((n) => (n.id === id ? { ...n, is_read: true, read_at: new Date().toISOString() } : n)))
  }

  const handleMarkAllRead = async () => {
    await notificationService.markAllRead()
    setNotifications((current) => current.map((n) => ({ ...n, is_read: true })))
  }

  const handleDelete = async (id: string) => {
    await notificationService.remove(id)
    setNotifications((current) => current.filter((n) => n.id !== id))
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Notifications</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Order, dispatch, and stock alerts.</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => {
              setUnreadOnly((v) => !v)
              setPage(1)
            }}
            className={`h-9 rounded-full border px-4 text-sm font-semibold transition ${
              unreadOnly
                ? 'border-primary-600 bg-primary-50 text-primary-700 dark:bg-primary-900/30'
                : 'border-neutral-200 text-neutral-600 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300'
            }`}
          >
            Unread only
          </button>
          <button
            type="button"
            onClick={() => void handleMarkAllRead()}
            className="inline-flex h-9 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300"
          >
            <CheckCheck className="h-4 w-4" />
            Mark all read
          </button>
        </div>
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        {isLoading ? (
          <div className="p-6 text-sm text-neutral-600 dark:text-neutral-400">Loading notifications...</div>
        ) : notifications.length === 0 ? (
          <div className="flex flex-col items-center gap-2 p-10 text-center text-sm text-neutral-500">
            <Bell className="h-8 w-8 text-neutral-300" />
            {unreadOnly ? 'No unread notifications.' : 'No notifications yet.'}
          </div>
        ) : (
          <div className="divide-y divide-neutral-100 dark:divide-neutral-800">
            {notifications.map((n) => {
              const Icon = TYPE_ICON[n.type] ?? Bell
              const isAlert = n.type === 'low_stock' || n.type === 'out_of_stock'
              const body = (
                <div className={`flex items-start gap-3 px-4 py-4 ${!n.is_read ? 'bg-primary-50/40 dark:bg-primary-900/10' : ''}`}>
                  <div className={`mt-0.5 rounded-full p-2 ${isAlert ? 'bg-amber-100 text-amber-700' : 'bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300'}`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <p className="truncate text-sm font-semibold text-neutral-900 dark:text-neutral-50">{n.title}</p>
                      {!n.is_read && <span className="h-2 w-2 shrink-0 rounded-full bg-primary-600" />}
                    </div>
                    <p className="mt-0.5 text-sm text-neutral-600 dark:text-neutral-400">{n.message}</p>
                    <p className="mt-1 text-xs text-neutral-400">{timeAgo(n.created_at)}</p>
                  </div>
                  <div className="flex shrink-0 gap-1">
                    {!n.is_read && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.preventDefault()
                          void handleMarkRead(n.id)
                        }}
                        title="Mark as read"
                        className="rounded-lg p-2 text-neutral-500 hover:bg-neutral-100 dark:hover:bg-neutral-800"
                      >
                        <Check className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={(e) => {
                        e.preventDefault()
                        void handleDelete(n.id)
                      }}
                      title="Delete"
                      className="rounded-lg p-2 text-neutral-500 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-950/30"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )
              return n.link ? (
                <Link key={n.id} to={n.link} onClick={() => !n.is_read && void handleMarkRead(n.id)} className="block hover:bg-neutral-50 dark:hover:bg-neutral-800/50">
                  {body}
                </Link>
              ) : (
                <div key={n.id}>{body}</div>
              )
            })}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-neutral-500">Page {page} of {Math.max(totalPages, 1)}</p>
        <div className="flex gap-2">
          <button type="button" disabled={page <= 1} onClick={() => setPage((v) => v - 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Previous</button>
          <button type="button" disabled={totalPages === 0 || page >= totalPages} onClick={() => setPage((v) => v + 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Next</button>
        </div>
      </div>
    </div>
  )
}
