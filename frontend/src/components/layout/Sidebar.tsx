import { NavLink } from 'react-router-dom'
import { getNavItemsForRole } from '@/constants/navigation'
import { brand } from '@/constants/colors'
import { cn } from '@/utils/cn'
import type { UserRole } from '@/types'

interface SidebarProps {
  role?: UserRole
  collapsed?: boolean
}

export function Sidebar({ role = 'founder', collapsed = false }: SidebarProps) {
  const navItems = getNavItemsForRole(role)

  return (
    <aside
      className={cn(
        'hidden lg:flex flex-col bg-white dark:bg-neutral-900 border-r border-neutral-200 dark:border-neutral-800 h-full transition-all duration-200',
        collapsed ? 'w-16' : 'w-60',
      )}
    >
      <div className={cn('flex items-center gap-3 px-4 h-16 border-b border-neutral-200 dark:border-neutral-800', collapsed && 'justify-center px-2')}>
        <div className="w-8 h-8 rounded-lg bg-primary-600 flex items-center justify-center shrink-0">
          <span className="text-white font-bold text-sm">A</span>
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="font-semibold text-sm text-neutral-900 dark:text-neutral-50 truncate">{brand.name}</p>
            <p className="text-xs text-neutral-600 dark:text-neutral-400 truncate">ERP Platform</p>
          </div>
        )}
      </div>

      <nav className="flex-1 overflow-y-auto scrollbar-thin py-4 px-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary-50 text-primary-600 dark:bg-primary-600/20 dark:text-primary-50'
                    : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900 dark:text-neutral-400 dark:hover:bg-neutral-800 dark:hover:text-neutral-50',
                  collapsed && 'justify-center px-2',
                )
              }
            >
              <Icon className="w-5 h-5 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          )
        })}
      </nav>

      <div className="p-4 border-t border-neutral-200 dark:border-neutral-800">
        {!collapsed && (
          <p className="text-xs text-neutral-600 dark:text-neutral-400 text-center">
            © {new Date().getFullYear()} {brand.name}
          </p>
        )}
      </div>
    </aside>
  )
}
