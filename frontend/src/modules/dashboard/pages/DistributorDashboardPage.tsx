import { MapPin, Plus, ShoppingCart, Store, Truck } from 'lucide-react'
import { useAuth } from '@/app/providers/AuthProvider'

const territories = ['Tambaram', 'Chromepet', 'Guduvanchery']

const tasks = [
  { title: 'Update delivery — Sri Murugan Stores', meta: 'Order # pending', action: 'Update Delivery' },
  { title: 'Follow up — New vendor registration', meta: 'Added yesterday', action: 'View Vendor' },
]

export function DistributorDashboardPage() {
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">
            Good morning, {user?.full_name?.split(' ')[0] ?? 'Distributor'}
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-1">
            Your field operations for today.
          </p>
        </div>
        <button
          type="button"
          className="inline-flex items-center justify-center gap-2 h-10 px-4 rounded-lg bg-primary-600 text-white text-sm font-medium hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" />
          Add Vendor
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {territories.map((territory) => (
          <span
            key={territory}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-primary-600/30 text-primary-600 text-xs font-medium bg-primary-50 dark:bg-primary-600/10"
          >
            <MapPin className="w-3 h-3" />
            {territory}
          </span>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: 'My Vendors', value: '0', icon: Store },
          { label: 'Pending Deliveries', value: '0', icon: Truck },
          { label: 'Orders This Week', value: '0', icon: ShoppingCart },
        ].map((item) => {
          const Icon = item.icon
          return (
            <div key={item.label} className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-surface-dark p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-neutral-600 dark:text-neutral-400">{item.label}</p>
                  <p className="text-2xl font-semibold mt-2">{item.value}</p>
                </div>
                <div className="w-10 h-10 rounded-lg bg-primary-50 dark:bg-primary-600/20 flex items-center justify-center">
                  <Icon className="w-5 h-5 text-primary-600" />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      <div className="rounded-xl border border-neutral-200 dark:border-neutral-800 bg-white dark:bg-surface-dark p-5">
        <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Today&apos;s Tasks</h3>
        <div className="mt-4 space-y-3">
          {tasks.map((task) => (
            <div
              key={task.title}
              className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 rounded-lg bg-neutral-50 dark:bg-neutral-800/50"
            >
              <div>
                <p className="font-medium text-sm text-neutral-900 dark:text-neutral-50">{task.title}</p>
                <p className="text-xs text-neutral-600 dark:text-neutral-400 mt-1">{task.meta}</p>
              </div>
              <button type="button" className="h-9 px-3 rounded-lg bg-primary-600 text-white text-xs font-medium">
                {task.action}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
