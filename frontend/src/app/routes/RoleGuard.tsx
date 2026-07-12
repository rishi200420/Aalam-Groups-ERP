import { Navigate } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { isDistributorRole, isFounderRole } from '@/types'
import type { ReactNode } from 'react'

interface RoleGuardProps {
  children: ReactNode
  allowed: 'founder' | 'distributor'
}

export function RoleGuard({ children, allowed }: RoleGuardProps) {
  const { primaryRole } = useAuth()

  if (allowed === 'founder' && !isFounderRole(primaryRole)) {
    return <Navigate to="/dashboard/distributor" replace />
  }

  if (allowed === 'distributor' && !isDistributorRole(primaryRole)) {
    return <Navigate to="/dashboard/founder" replace />
  }

  return children
}
