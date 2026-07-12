import type { DispatchTimelineEntry } from '@/types'

interface DispatchTimelineProps {
  entries: DispatchTimelineEntry[]
}

export function DispatchTimeline({ entries }: DispatchTimelineProps) {
  if (!entries?.length) {
    return <p className="text-sm text-neutral-600 dark:text-neutral-400">No timeline entries yet.</p>
  }

  return (
    <div className="space-y-3">
      {entries.map((entry) => (
        <div key={entry.id} className="flex gap-3 rounded-lg border border-neutral-200 bg-neutral-50 p-3 dark:border-neutral-800 dark:bg-neutral-900/60">
          <div className="mt-1.5 h-2.5 w-2.5 flex-none rounded-full bg-primary-600" />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-sm font-medium text-neutral-900 dark:text-neutral-50">{entry.status}</p>
              <span className="text-xs text-neutral-500">{new Date(entry.changed_at).toLocaleString()}</span>
            </div>
            {entry.notes ? <p className="mt-1 text-sm text-neutral-700 dark:text-neutral-300">{entry.notes}</p> : null}
            {entry.changed_by ? <p className="mt-1 text-xs text-neutral-500">Updated by {entry.changed_by}</p> : null}
          </div>
        </div>
      ))}
    </div>
  )
}
