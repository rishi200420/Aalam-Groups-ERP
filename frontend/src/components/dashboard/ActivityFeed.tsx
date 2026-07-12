import { Activity } from 'lucide-react'
import type { DashboardActivity } from '@/types'

interface ActivityFeedProps {
  activities: DashboardActivity[]
  isLoading?: boolean
}

export function ActivityFeed({ activities, isLoading }: ActivityFeedProps) {
  return (
    <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-surface-dark p-5 h-full">
      <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Recent Activity</h3>
      {isLoading ? (
        <div className="mt-4 space-y-3">
          {[...Array(4)].map((_, index) => (
            <div key={index} className="h-8 animate-pulse rounded-lg bg-neutral-100 dark:bg-neutral-800" />
          ))}
        </div>
      ) : activities.length === 0 ? (
        <p className="mt-4 text-sm text-neutral-500">No recent activity yet.</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {activities.map((activity, index) => (
            <li key={`${activity.created_at}-${index}`} className="flex items-start gap-2.5">
              <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-50 dark:bg-primary-600/20">
                <Activity className="h-3.5 w-3.5 text-primary-600" />
              </span>
              <div className="min-w-0">
                <p className="truncate text-sm text-neutral-700 dark:text-neutral-300">{activity.message}</p>
                <p className="text-xs text-neutral-400">{new Date(activity.created_at).toLocaleString()}</p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
