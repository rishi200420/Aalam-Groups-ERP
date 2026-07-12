import {
  BarChart3,
  Bell,
  Boxes,
  LayoutDashboard,
  Package,
  Settings,
  ShoppingCart,
  Store,
  Truck,
  Users,
} from 'lucide-react'

export type UserRole = 'super_admin' | 'founder' | 'distributor' | 'warehouse' | 'sales_executive'

export interface NavItem {
  label: string
  path: string
  icon: typeof LayoutDashboard
  roles: UserRole[]
}

export const founderNavItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ['founder'] },
  { label: 'Outlets', path: '/outlets', icon: Store, roles: ['founder'] },
  { label: 'Products', path: '/products', icon: Package, roles: ['founder'] },
  { label: 'Orders', path: '/orders', icon: ShoppingCart, roles: ['founder'] },
  { label: 'Dispatch', path: '/dispatch', icon: Truck, roles: ['founder'] },
  { label: 'Inventory', path: '/inventory', icon: Boxes, roles: ['founder'] },
  { label: 'Reports', path: '/reports', icon: BarChart3, roles: ['founder'] },
  { label: 'Users', path: '/users', icon: Users, roles: ['founder'] },
  { label: 'Settings', path: '/settings', icon: Settings, roles: ['founder'] },
]

export const distributorNavItems: NavItem[] = [
  { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard, roles: ['distributor'] },
  { label: 'My Outlets', path: '/outlets', icon: Store, roles: ['distributor'] },
  { label: 'Orders', path: '/orders', icon: ShoppingCart, roles: ['distributor'] },
  { label: 'Deliveries', path: '/dispatch', icon: Truck, roles: ['distributor'] },
]

export const mobileNavItems: NavItem[] = [
  { label: 'Home', path: '/dashboard', icon: LayoutDashboard, roles: ['founder', 'distributor'] },
  { label: 'Outlets', path: '/outlets', icon: Store, roles: ['founder', 'distributor'] },
  { label: 'Orders', path: '/orders', icon: ShoppingCart, roles: ['founder', 'distributor'] },
  { label: 'Dispatch', path: '/dispatch', icon: Truck, roles: ['founder', 'distributor'] },
  { label: 'More', path: '/settings', icon: Settings, roles: ['founder', 'distributor'] },
]

export const headerActions = {
  notifications: { label: 'Notifications', path: '/notifications', icon: Bell },
  profile: { label: 'Profile', path: '/profile', icon: Users },
}

export function getNavItemsForRole(role: UserRole): NavItem[] {
  if (role === 'founder') return founderNavItems
  if (role === 'distributor') return distributorNavItems
  return founderNavItems
}
