import { Outlet } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { MainLayout } from '@/components/layout/MainLayout'
import type { UserRole } from '@/types'
import { isDistributorRole, isFounderRole } from '@/types'

interface AppLayoutProps {
  title?: string
  role?: UserRole
}

export function AppLayout({ title, role }: AppLayoutProps) {
  const { primaryRole } = useAuth()
  const resolvedRole: UserRole = role ?? (
    isFounderRole(primaryRole) ? 'founder' : isDistributorRole(primaryRole) ? 'distributor' : 'founder'
  )

  return (
    <MainLayout title={title} role={resolvedRole}>
      <Outlet />
    </MainLayout>
  )
}
