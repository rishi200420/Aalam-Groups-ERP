import { Bell, LogOut, Menu, Moon, Settings, Sun, UserCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { useBrandFilter } from '@/app/providers/BrandFilterProvider'
import { useTheme } from '@/app/providers/ThemeProvider'
import { brand } from '@/constants/colors'
import { notificationService } from '@/services/notification.service'

interface HeaderProps {
  title?: string
  onMenuClick?: () => void
  showMenuButton?: boolean
}

export function Header({ title = 'Dashboard', onMenuClick, showMenuButton = false }: HeaderProps) {
  const { theme, toggleTheme } = useTheme()
  const { user, logout } = useAuth()
  const { brand: brandFilter, setBrand: setBrandFilter } = useBrandFilter()
  const navigate = useNavigate()
  const [isProfileOpen, setIsProfileOpen] = useState(false)
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    let isMounted = true
    const loadUnreadCount = async () => {
      try {
        const response = await notificationService.unreadCount()
        if (isMounted) setUnreadCount(response.data?.unread_count ?? 0)
      } catch {
        // silently ignore; the bell simply shows no badge
      }
    }
    void loadUnreadCount()
    const interval = setInterval(loadUnreadCount, 30000)
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [])

  const handleLogout = async () => {
    try {
      await logout()
    } finally {
      navigate('/login', { replace: true })
    }
  }

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-4 lg:px-6 bg-white dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-800">
      <div className="flex items-center gap-3 min-w-0">
        {showMenuButton && (
          <button
            type="button"
            onClick={onMenuClick}
            className="lg:hidden p-2 rounded-lg text-neutral-600 hover:bg-neutral-50 dark:text-neutral-400 dark:hover:bg-neutral-800"
            aria-label="Open menu"
          >
            <Menu className="w-5 h-5" />
          </button>
        )}
        <div className="min-w-0">
          <h1 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50 truncate">{title}</h1>
          <p className="hidden sm:block text-xs text-neutral-600 dark:text-neutral-400 truncate">
            {user?.full_name ? `${user.full_name} · ${brand.appName}` : brand.appName}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1 sm:gap-2">
        <select
          className="hidden md:block text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg px-2 py-1.5 bg-white dark:bg-neutral-800 text-neutral-900 dark:text-neutral-50"
          value={brandFilter}
          onChange={(event) => setBrandFilter(event.target.value as typeof brandFilter)}
          aria-label="Select brand"
        >
          <option value="all">All Brands</option>
          <option value="tastiq">TASTIQ</option>
          <option value="lemuria">LEMURIA</option>
        </select>

        <button
          type="button"
          onClick={toggleTheme}
          className="p-2 rounded-lg text-neutral-600 hover:bg-neutral-50 dark:text-neutral-400 dark:hover:bg-neutral-800"
          aria-label="Toggle dark mode"
        >
          {theme === 'light' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
        </button>

        <Link
          to="/notifications"
          className="relative p-2 rounded-lg text-neutral-600 hover:bg-neutral-50 dark:text-neutral-400 dark:hover:bg-neutral-800"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          {unreadCount > 0 && (
            <span className="absolute top-0.5 right-0.5 flex h-4 min-w-[1rem] items-center justify-center rounded-full bg-gold-500 px-1 text-[10px] font-semibold text-white">
              {unreadCount > 99 ? '99+' : unreadCount}
            </span>
          )}
        </Link>

        <div className="relative">
          <button
            type="button"
            onClick={() => setIsProfileOpen((open) => !open)}
            className="p-2 rounded-lg text-neutral-600 hover:bg-neutral-50 dark:text-neutral-400 dark:hover:bg-neutral-800"
            aria-label="Profile menu"
          >
            <UserCircle className="w-5 h-5" />
          </button>
          {isProfileOpen && (
            <>
              <button
                type="button"
                className="fixed inset-0 z-40 cursor-default"
                aria-label="Close menu"
                onClick={() => setIsProfileOpen(false)}
              />
              <div className="absolute right-0 z-50 mt-2 w-56 rounded-lg border border-neutral-200 bg-white py-1 shadow-lg dark:border-neutral-800 dark:bg-neutral-900">
                <div className="border-b border-neutral-100 px-3 py-2 dark:border-neutral-800">
                  <p className="truncate text-sm font-medium text-neutral-900 dark:text-neutral-50">{user?.full_name}</p>
                  <p className="truncate text-xs text-neutral-500">{user?.email}</p>
                </div>
                <Link
                  to="/profile"
                  onClick={() => setIsProfileOpen(false)}
                  className="flex items-center gap-2 px-3 py-2 text-sm text-neutral-700 hover:bg-neutral-50 dark:text-neutral-300 dark:hover:bg-neutral-800"
                >
                  <UserCircle className="h-4 w-4" /> Profile
                </Link>
                <Link
                  to="/settings"
                  onClick={() => setIsProfileOpen(false)}
                  className="flex items-center gap-2 px-3 py-2 text-sm text-neutral-700 hover:bg-neutral-50 dark:text-neutral-300 dark:hover:bg-neutral-800"
                >
                  <Settings className="h-4 w-4" /> Settings
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setIsProfileOpen(false)
                    void handleLogout()
                  }}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/30"
                >
                  <LogOut className="h-4 w-4" /> Logout
                </button>
              </div>
            </>
          )}
        </div>

        <button
          type="button"
          onClick={() => void handleLogout()}
          className="p-2 rounded-lg text-neutral-600 hover:bg-red-50 hover:text-red-600 dark:text-neutral-400 dark:hover:bg-red-950/30 dark:hover:text-red-400"
          aria-label="Logout"
          title="Logout"
        >
          <LogOut className="w-5 h-5" />
        </button>
      </div>
    </header>
  )
}
