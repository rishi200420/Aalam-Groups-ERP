import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from '@/components/layout/AppLayout'
import { ProtectedRoute, GuestRoute, RoleDashboardRedirect } from '@/app/routes/ProtectedRoute'
import { RoleGuard } from '@/app/routes/RoleGuard'
import { SplashPage } from '@/modules/auth/pages/SplashPage'
import { LoginPage } from '@/modules/auth/pages/LoginPage'
import { ForgotPasswordPage } from '@/modules/auth/pages/ForgotPasswordPage'
import { FounderDashboardPage } from '@/modules/dashboard/pages/FounderDashboardPage'
import { DistributorDashboardPage } from '@/modules/dashboard/pages/DistributorDashboardPage'
import { OutletListPage } from '@/modules/outlets/pages/OutletListPage'
import { OutletDetailPage } from '@/modules/outlets/pages/OutletDetailPage'
import { OutletFormPage } from '@/modules/outlets/pages/OutletFormPage'
import { ProductListPage } from '@/modules/products/pages/ProductListPage'
import { ProductFormPage } from '@/modules/products/pages/ProductFormPage'
import { UserManagementPage } from '@/modules/users/pages/UserManagementPage'
import { OrderListPage } from '@/modules/orders/pages/OrderListPage'
import { OrderFormPage } from '@/modules/orders/pages/OrderFormPage'
import { OrderDetailPage } from '@/modules/orders/pages/OrderDetailPage'
import { DispatchListPage } from '@/modules/dispatch/pages/DispatchListPage'
import { DispatchDetailPage } from '@/modules/dispatch/pages/DispatchDetailPage'
import { CreateDispatchPage } from '@/modules/dispatch/pages/CreateDispatchPage'
import { InventoryDetailPage } from '@/modules/inventory/pages/InventoryDetailPage'
import { InventoryFormPage } from '@/modules/inventory/pages/InventoryFormPage'
import { InventoryListPage } from '@/modules/inventory/pages/InventoryListPage'
import { NotificationsPage } from '@/modules/notifications/pages/NotificationsPage'
import { ProfilePage } from '@/modules/profile/pages/ProfilePage'
import { ReportsPage } from '@/modules/reports/pages/ReportsPage'
import { SettingsPage } from '@/modules/settings/pages/SettingsPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<SplashPage />} />

      <Route element={<GuestRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<RoleDashboardRedirect />} />

        <Route element={<AppLayout />}>
          <Route
            path="/dashboard/founder"
            element={
              <RoleGuard allowed="founder">
                <FounderDashboardPage />
              </RoleGuard>
            }
          />
          <Route
            path="/dashboard/distributor"
            element={
              <RoleGuard allowed="distributor">
                <DistributorDashboardPage />
              </RoleGuard>
            }
          />
          <Route path="/outlets" element={<OutletListPage />} />
          <Route path="/outlets/new" element={<OutletFormPage />} />
          <Route path="/outlets/:id" element={<OutletDetailPage />} />
          <Route path="/outlets/:id/edit" element={<OutletFormPage />} />
          <Route path="/products" element={<ProductListPage />} />
          <Route path="/products/new" element={<ProductFormPage />} />
          <Route path="/products/:id/edit" element={<ProductFormPage />} />
          <Route path="/orders" element={<OrderListPage />} />
          <Route path="/orders/new" element={<OrderFormPage />} />
          <Route path="/orders/:id" element={<OrderDetailPage />} />
          <Route path="/dispatch" element={<DispatchListPage />} />
          <Route path="/dispatch/create" element={<CreateDispatchPage />} />
          <Route path="/dispatch/:id" element={<DispatchDetailPage />} />
          <Route path="/inventory" element={<InventoryListPage />} />
          <Route path="/inventory/new" element={<InventoryFormPage />} />
          <Route path="/inventory/:id" element={<InventoryDetailPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/users" element={<UserManagementPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
