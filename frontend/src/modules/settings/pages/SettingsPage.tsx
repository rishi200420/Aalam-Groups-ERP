import { Bell, Building2, Save } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { useAuth } from '@/app/providers/AuthProvider'
import { settingsService } from '@/services/settings.service'
import type { NotificationPreference, SystemSettings } from '@/types'

const PREFERENCE_ROWS: { key: keyof NotificationPreference; label: string; description: string }[] = [
  { key: 'notify_orders', label: 'Orders', description: 'New orders, approvals, cancellations, and deliveries.' },
  { key: 'notify_dispatch', label: 'Dispatch', description: 'Dispatch delivered or failed alerts.' },
  { key: 'notify_stock', label: 'Stock alerts', description: 'Low stock and out-of-stock warnings.' },
  { key: 'notify_system', label: 'System', description: 'General system notifications.' },
]

export function SettingsPage() {
  const { isFounder } = useAuth()

  const [systemSettings, setSystemSettings] = useState<SystemSettings | null>(null)
  const [systemForm, setSystemForm] = useState<SystemSettings | null>(null)
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null)

  const [isLoading, setIsLoading] = useState(true)
  const [isSavingSystem, setIsSavingSystem] = useState(false)
  const [isSavingPreferences, setIsSavingPreferences] = useState(false)
  const [systemSaved, setSystemSaved] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const load = async () => {
      setIsLoading(true)
      try {
        const requests: Promise<unknown>[] = [settingsService.getNotificationPreferences().then((r) => setPreferences(r.data ?? null))]
        if (isFounder) {
          requests.push(
            settingsService.getSystemSettings().then((r) => {
              setSystemSettings(r.data ?? null)
              setSystemForm(r.data ?? null)
            }),
          )
        }
        await Promise.all(requests)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load settings')
      } finally {
        setIsLoading(false)
      }
    }
    void load()
  }, [isFounder])

  const submitSystemSettings = async (event: FormEvent) => {
    event.preventDefault()
    if (!systemForm) return
    setIsSavingSystem(true)
    setError('')
    setSystemSaved(false)
    try {
      const response = await settingsService.updateSystemSettings(systemForm)
      setSystemSettings(response.data ?? null)
      setSystemForm(response.data ?? null)
      setSystemSaved(true)
      setTimeout(() => setSystemSaved(false), 2500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save system settings')
    } finally {
      setIsSavingSystem(false)
    }
  }

  const togglePreference = async (key: keyof NotificationPreference) => {
    if (!preferences) return
    const next = { ...preferences, [key]: !preferences[key] }
    setPreferences(next)
    setIsSavingPreferences(true)
    try {
      await settingsService.updateNotificationPreferences({ [key]: next[key] })
    } catch (err) {
      setPreferences(preferences) // revert on failure
      setError(err instanceof Error ? err.message : 'Failed to update notification preference')
    } finally {
      setIsSavingPreferences(false)
    }
  }

  if (isLoading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-600 dark:border-neutral-800 dark:bg-surface-dark dark:text-neutral-400">Loading settings...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Settings</h2>
        <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">Manage business profile and notification preferences.</p>
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      {isFounder && systemForm && (
        <form onSubmit={submitSystemSettings} className="space-y-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
          <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900 dark:text-neutral-50">
            <Building2 className="h-4 w-4" />
            Business Profile
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Business Name</label>
              <input
                value={systemForm.business_name}
                onChange={(e) => setSystemForm({ ...systemForm, business_name: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">GST Number</label>
              <input
                value={systemForm.gst_number ?? ''}
                onChange={(e) => setSystemForm({ ...systemForm, gst_number: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Support Email</label>
              <input
                type="email"
                value={systemForm.support_email ?? ''}
                onChange={(e) => setSystemForm({ ...systemForm, support_email: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Support Phone</label>
              <input
                value={systemForm.support_phone ?? ''}
                onChange={(e) => setSystemForm({ ...systemForm, support_phone: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Default Currency</label>
              <input
                value={systemForm.default_currency}
                onChange={(e) => setSystemForm({ ...systemForm, default_currency: e.target.value })}
                className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Default Low-Stock Threshold</label>
              <input
                type="number"
                min={0}
                value={systemForm.low_stock_default_threshold}
                onChange={(e) => setSystemForm({ ...systemForm, low_stock_default_threshold: Number(e.target.value) })}
                className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
              />
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Address</label>
            <textarea
              value={systemForm.address ?? ''}
              onChange={(e) => setSystemForm({ ...systemForm, address: e.target.value })}
              className="mt-1 h-20 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Invoice Footer Note</label>
            <textarea
              value={systemForm.invoice_footer_note ?? ''}
              onChange={(e) => setSystemForm({ ...systemForm, invoice_footer_note: e.target.value })}
              placeholder="e.g. Thank you for your business!"
              className="mt-1 h-16 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>

          <div className="flex items-center justify-end gap-3">
            {systemSaved && <span className="text-sm font-medium text-emerald-600">Saved</span>}
            <button
              type="button"
              onClick={() => setSystemForm(systemSettings)}
              className="h-10 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 dark:border-neutral-700 dark:text-neutral-300"
            >
              Reset
            </button>
            <button
              type="submit"
              disabled={isSavingSystem}
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-60"
            >
              <Save className="h-4 w-4" />
              {isSavingSystem ? 'Saving...' : 'Save changes'}
            </button>
          </div>
        </form>
      )}

      {preferences && (
        <div className="space-y-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
          <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900 dark:text-neutral-50">
            <Bell className="h-4 w-4" />
            Notification Preferences
          </div>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Choose which alerts you want to receive in-app.</p>
          <div className="divide-y divide-neutral-100 dark:divide-neutral-800">
            {PREFERENCE_ROWS.map((row) => (
              <div key={row.key} className="flex items-center justify-between py-3">
                <div>
                  <p className="text-sm font-medium text-neutral-900 dark:text-neutral-50">{row.label}</p>
                  <p className="text-xs text-neutral-500">{row.description}</p>
                </div>
                <button
                  type="button"
                  role="switch"
                  aria-checked={preferences[row.key]}
                  disabled={isSavingPreferences}
                  onClick={() => void togglePreference(row.key)}
                  className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${preferences[row.key] ? 'bg-primary-600' : 'bg-neutral-300 dark:bg-neutral-700'}`}
                >
                  <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-transform ${preferences[row.key] ? 'translate-x-5' : 'translate-x-0.5'}`} />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
