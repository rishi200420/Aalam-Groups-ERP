import type { DispatchStatus } from '@/types'

interface DispatchStatusBadgeProps {
  status: DispatchStatus
}

const statusStyles: Record<DispatchStatus, string> = {
  ready: 'bg-amber-100 text-amber-800',
  dispatched: 'bg-purple-100 text-purple-800',
  in_transit: 'bg-indigo-100 text-indigo-800',
  delivered: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  returned: 'bg-neutral-100 text-neutral-800',
}

const statusLabels: Record<DispatchStatus, string> = {
  ready: 'Ready',
  dispatched: 'Dispatched',
  in_transit: 'In Transit',
  delivered: 'Delivered',
  failed: 'Failed',
  returned: 'Returned',
}

export function DispatchStatusBadge({ status }: DispatchStatusBadgeProps) {
  return (
    <span className={`inline-flex w-fit items-center rounded px-2 py-1 text-xs font-medium capitalize ${statusStyles[status]}`}>
      {statusLabels[status]}
    </span>
  )
}
