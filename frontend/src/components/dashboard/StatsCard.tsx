import type { LucideIcon } from 'lucide-react'

interface StatsCardProps {
  label: string
  value: string
  icon: LucideIcon
  trend?: string
  isLoading?: boolean
  onClick?: () => void
}

export function StatsCard({ label, value, icon: Icon, trend, isLoading, onClick }: StatsCardProps) {
  const Wrapper = onClick ? 'button' : 'div'
  return (
    <Wrapper
      type={onClick ? 'button' : undefined}
      onClick={onClick}
      className={`h-full w-full rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-surface-dark p-5 text-left transition-shadow ${onClick ? 'hover:shadow-md cursor-pointer' : ''}`}
    >
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <p className="text-sm text-neutral-600 dark:text-neutral-400">{label}</p>
          {isLoading ? (
            <div className="mt-2 h-7 w-20 animate-pulse rounded bg-neutral-200 dark:bg-neutral-700" />
          ) : (
            <p className="mt-2 text-2xl font-semibold text-neutral-900 dark:text-neutral-50 transition-all duration-300">
              {value}
            </p>
          )}
          {trend && !isLoading && <p className="text-xs text-primary-600 mt-1">{trend}</p>}
        </div>
        <div className="w-10 h-10 rounded-lg bg-primary-50 dark:bg-primary-600/20 flex items-center justify-center shrink-0">
          <Icon className="w-5 h-5 text-primary-600" />
        </div>
      </div>
    </Wrapper>
  )
}
