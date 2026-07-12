import { Key, Plus, Power, Trash2, UserCog, X } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { userManagementService } from '@/services/user-management.service'
import type { ManagedUser, ManagedUserCreatePayload, ProductBrand, UserRole } from '@/types'

const emptyForm: ManagedUserCreatePayload = {
  full_name: '',
  email: '',
  phone: '',
  password: '',
  role: 'distributor',
  employee_id: '',
  distributor_code: '',
  territory: '',
  brand: undefined,
}

const roleLabels: Record<UserRole, string> = {
  super_admin: 'Super Admin',
  founder: 'Founder',
  distributor: 'Distributor',
  warehouse: 'Warehouse',
  sales_executive: 'Sales Executive',
}

export function UserManagementPage() {
  const [users, setUsers] = useState<ManagedUser[]>([])
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<ManagedUser | null>(null)
  const [form, setForm] = useState<ManagedUserCreatePayload>(emptyForm)
  const [error, setError] = useState<string | null>(null)
  const [isSaving, setIsSaving] = useState(false)
  const [resetTarget, setResetTarget] = useState<ManagedUser | null>(null)
  const [resetPassword, setResetPassword] = useState('')

  const loadUsers = () => {
    setIsLoading(true)
    void userManagementService
      .list({ page, page_size: 10, search: search || undefined, role: roleFilter || undefined })
      .then((response) => {
        setUsers(response.data ?? [])
        setTotalPages(response.total_pages)
      })
      .finally(() => setIsLoading(false))
  }

  useEffect(loadUsers, [page, search, roleFilter])

  const openCreate = () => {
    setEditingUser(null)
    setForm(emptyForm)
    setError(null)
    setIsModalOpen(true)
  }

  const openEdit = (user: ManagedUser) => {
    setEditingUser(user)
    setForm({
      full_name: user.full_name,
      email: user.email,
      phone: user.phone ?? '',
      password: '',
      role: user.role,
      employee_id: user.employee_id ?? '',
      distributor_code: user.distributor_code ?? '',
      territory: user.territory ?? '',
      brand: user.brand ?? undefined,
    })
    setError(null)
    setIsModalOpen(true)
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setIsSaving(true)
    setError(null)
    try {
      if (editingUser) {
        await userManagementService.update(editingUser.id, {
          full_name: form.full_name,
          phone: form.phone,
          role: form.role,
          employee_id: form.employee_id || undefined,
          distributor_code: form.distributor_code || undefined,
          territory: form.territory || undefined,
          brand: form.brand,
        })
      } else {
        await userManagementService.create(form)
      }
      setIsModalOpen(false)
      loadUsers()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save user.')
    } finally {
      setIsSaving(false)
    }
  }

  const toggleActive = async (user: ManagedUser) => {
    if (user.is_active) {
      await userManagementService.deactivate(user.id)
    } else {
      await userManagementService.activate(user.id)
    }
    loadUsers()
  }

  const removeUser = async (user: ManagedUser) => {
    if (!window.confirm(`Delete ${user.full_name}? This cannot be undone.`)) return
    try {
      await userManagementService.remove(user.id)
      loadUsers()
    } catch (err) {
      window.alert(err instanceof Error ? err.message : 'Unable to delete user.')
    }
  }

  const submitReset = async (event: FormEvent) => {
    event.preventDefault()
    if (!resetTarget) return
    await userManagementService.resetPassword(resetTarget.id, resetPassword)
    setResetTarget(null)
    setResetPassword('')
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">User Management</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Create distributor accounts and manage founder-level access.</p>
        </div>
        <button type="button" onClick={openCreate} className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700">
          <Plus className="h-4 w-4" />
          Create User
        </button>
      </div>

      <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark sm:grid-cols-[1fr_200px]">
        <input
          value={search}
          onChange={(event) => { setSearch(event.target.value); setPage(1) }}
          placeholder="Search name, email, employee ID"
          className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
        />
        <select value={roleFilter} onChange={(event) => { setRoleFilter(event.target.value); setPage(1) }} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
          <option value="">All Roles</option>
          {Object.entries(roleLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </div>

      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        <div className="hidden grid-cols-[1.4fr_1fr_1fr_1fr_140px] gap-4 border-b border-neutral-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-neutral-500 md:grid">
          <span>User</span>
          <span>Role</span>
          <span>Territory / Brand</span>
          <span>Status</span>
          <span>Actions</span>
        </div>
        {isLoading ? (
          <div className="p-6 text-sm text-neutral-600">Loading users...</div>
        ) : users.length === 0 ? (
          <div className="p-6 text-sm text-neutral-600">No users found.</div>
        ) : (
          users.map((user) => (
            <div key={user.id} className="grid gap-3 border-b border-neutral-100 px-4 py-4 last:border-0 md:grid-cols-[1.4fr_1fr_1fr_1fr_140px] md:items-center">
              <div>
                <p className="font-semibold text-neutral-900 dark:text-neutral-50">{user.full_name}</p>
                <p className="text-xs text-neutral-500">{user.email}{user.employee_id ? ` · ${user.employee_id}` : ''}</p>
              </div>
              <span className="text-sm text-neutral-700 dark:text-neutral-300">{roleLabels[user.role]}</span>
              <span className="text-sm text-neutral-700 dark:text-neutral-300">
                {user.territory ?? '—'}{user.brand ? ` · ${user.brand}` : ''}
              </span>
              <span className={`inline-flex w-fit items-center rounded px-2 py-1 text-xs font-medium ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-neutral-200 text-neutral-700'}`}>
                {user.is_active ? 'Active' : 'Inactive'}
              </span>
              <div className="flex items-center gap-2">
                <button type="button" title="Edit" onClick={() => openEdit(user)} className="rounded-lg border border-neutral-200 p-2 hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
                  <UserCog className="h-4 w-4" />
                </button>
                <button type="button" title="Reset password" onClick={() => setResetTarget(user)} className="rounded-lg border border-neutral-200 p-2 hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
                  <Key className="h-4 w-4" />
                </button>
                <button type="button" title={user.is_active ? 'Deactivate' : 'Activate'} onClick={() => void toggleActive(user)} className="rounded-lg border border-neutral-200 p-2 hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800">
                  <Power className="h-4 w-4" />
                </button>
                <button type="button" title="Delete" onClick={() => void removeUser(user)} className="rounded-lg border border-red-200 p-2 text-red-600 hover:bg-red-50">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-neutral-500">Page {page} of {Math.max(totalPages, 1)}</p>
        <div className="flex gap-2">
          <button type="button" disabled={page <= 1} onClick={() => setPage((value) => value - 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Previous</button>
          <button type="button" disabled={totalPages === 0 || page >= totalPages} onClick={() => setPage((value) => value + 1)} className="h-9 rounded-lg border border-neutral-200 px-3 text-sm disabled:opacity-50">Next</button>
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-lg rounded-xl bg-white p-6 dark:bg-surface-dark">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">
                {editingUser ? 'Edit User' : 'Create User'}
              </h3>
              <button type="button" onClick={() => setIsModalOpen(false)} className="text-neutral-400 hover:text-neutral-600">
                <X className="h-5 w-5" />
              </button>
            </div>

            {error && <div className="mb-3 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>}

            <form onSubmit={(event) => void submit(event)} className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300 sm:col-span-2">
                Full Name
                <input required value={form.full_name} onChange={(event) => setForm((f) => ({ ...f, full_name: event.target.value }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              </label>
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300 sm:col-span-2">
                Email
                <input required type="email" disabled={!!editingUser} value={form.email} onChange={(event) => setForm((f) => ({ ...f, email: event.target.value }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm disabled:bg-neutral-100 dark:border-neutral-700 dark:bg-neutral-900" />
              </label>
              {!editingUser && (
                <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300 sm:col-span-2">
                  Password
                  <input required type="password" minLength={8} value={form.password} onChange={(event) => setForm((f) => ({ ...f, password: event.target.value }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
                </label>
              )}
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Phone
                <input value={form.phone ?? ''} onChange={(event) => setForm((f) => ({ ...f, phone: event.target.value }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              </label>
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Role
                <select value={form.role} onChange={(event) => setForm((f) => ({ ...f, role: event.target.value as UserRole }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
                  {Object.entries(roleLabels).filter(([value]) => value !== 'super_admin').map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </label>
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Employee ID
                <input value={form.employee_id ?? ''} onChange={(event) => setForm((f) => ({ ...f, employee_id: event.target.value }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              </label>
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Distributor Code
                <input value={form.distributor_code ?? ''} onChange={(event) => setForm((f) => ({ ...f, distributor_code: event.target.value }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              </label>
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Territory
                <input value={form.territory ?? ''} onChange={(event) => setForm((f) => ({ ...f, territory: event.target.value }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              </label>
              <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                Brand
                <select value={form.brand ?? ''} onChange={(event) => setForm((f) => ({ ...f, brand: (event.target.value || undefined) as ProductBrand | undefined }))} className="mt-1 h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
                  <option value="">Unassigned</option>
                  <option value="TASTIQ">TASTIQ</option>
                  <option value="LEMURIA">LEMURIA</option>
                </select>
              </label>

              <div className="sm:col-span-2 mt-2 flex justify-end gap-2">
                <button type="button" onClick={() => setIsModalOpen(false)} className="h-10 rounded-lg border border-neutral-200 px-4 text-sm">Cancel</button>
                <button type="submit" disabled={isSaving} className="h-10 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60">
                  {isSaving ? 'Saving...' : 'Save'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {resetTarget && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-xl bg-white p-6 dark:bg-surface-dark">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">Reset Password</h3>
              <button type="button" onClick={() => setResetTarget(null)} className="text-neutral-400 hover:text-neutral-600">
                <X className="h-5 w-5" />
              </button>
            </div>
            <p className="mb-3 text-sm text-neutral-600 dark:text-neutral-400">Set a new password for {resetTarget.full_name}.</p>
            <form onSubmit={(event) => void submitReset(event)} className="space-y-3">
              <input required type="password" minLength={8} value={resetPassword} onChange={(event) => setResetPassword(event.target.value)} placeholder="New password" className="h-10 w-full rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setResetTarget(null)} className="h-10 rounded-lg border border-neutral-200 px-4 text-sm">Cancel</button>
                <button type="submit" className="h-10 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700">Reset</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
