import { useState, type ReactNode } from 'react'
import { Sidebar } from '@/components/layout/Sidebar'
import { Header } from '@/components/layout/Header'
import { MobileNav } from '@/components/layout/MobileNav'
import type { UserRole } from '@/types'

interface MainLayoutProps {
  children: ReactNode
  title?: string
  role?: UserRole
}

export function MainLayout({ children, title, role = 'founder' }: MainLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen overflow-hidden bg-background dark:bg-background-dark">
      {/* Desktop sidebar */}
      <Sidebar role={role} />

      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-40 flex">
          <button
            type="button"
            className="fixed inset-0 bg-black/40"
            onClick={() => setSidebarOpen(false)}
            aria-label="Close sidebar overlay"
          />
          <div className="relative z-50 w-60 h-full">
            <Sidebar role={role} />
          </div>
        </div>
      )}

      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header
          title={title}
          showMenuButton
          onMenuClick={() => setSidebarOpen(true)}
        />

        <main className="flex-1 overflow-y-auto p-4 lg:p-6 pb-20 lg:pb-6">
          {children}
        </main>

        <MobileNav />
      </div>
    </div>
  )
}
