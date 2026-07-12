import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background dark:bg-background-dark">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 rounded-full border-2 border-primary-600 border-t-transparent animate-spin" />
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Loading session...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return <Outlet />
}

export function GuestRoute() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background dark:bg-background-dark">
        <div className="w-10 h-10 rounded-full border-2 border-primary-600 border-t-transparent animate-spin" />
      </div>
    )
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export function RoleDashboardRedirect() {
  const { isFounder, isDistributor } = useAuth()

  if (isFounder) {
    return <Navigate to="/dashboard/founder" replace />
  }

  if (isDistributor) {
    return <Navigate to="/dashboard/distributor" replace />
  }

  return <Navigate to="/dashboard/founder" replace />
}
