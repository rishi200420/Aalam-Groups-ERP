import { Eye, MapPin, Phone, Plus, Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { outletService } from '@/services/outlet.service'
import type { Outlet } from '@/types'

const typeLabels: Record<string, string> = {
  tea_shop: 'Tea Shop',
  cafe: 'Cafe',
  bakery: 'Bakery',
  restaurant: 'Restaurant',
  hotel: 'Hotel',
  supermarket: 'Supermarket',
  general_store: 'General Store',
}

export function OutletListPage() {
  const [outlets, setOutlets] = useState<Outlet[]>([])
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [businessType, setBusinessType] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsLoading(true)
    void outletService
      .list({ page, page_size: 10, search: search || undefined, status: status || undefined, business_type: businessType || undefined })
      .then((response) => {
        setOutlets(response.data ?? [])
        setTotalPages(response.total_pages)
      })
      .finally(() => setIsLoading(false))
  }, [page, search, status, businessType])

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Outlet Management</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Search, assign, visit, and manage Aalam Groups outlets.</p>
        </div>
        <Link to="/outlets/new" className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700">
          <Plus className="h-4 w-4" />
          Add Outlet
        </Link>
      </div>

      <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark md:grid-cols-[1fr_180px_200px]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          <input value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} placeholder="Search outlet, owner, phone, area" className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-10 pr-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
        </div>
        <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1) }} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="blocked">Blocked</option>
        </select>
        <select value={businessType} onChange={(event) => { setBusinessType(event.target.value); setPage(1) }} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
          <option value="">All Business Types</option>
          {Object.entries(typeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
      </div>

      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        <div className="hidden grid-cols-[1.4fr_1fr_1fr_1fr_120px] gap-4 border-b border-neutral-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-neutral-500 md:grid">
          <span>Outlet</span>
          <span>Owner</span>
          <span>Territory</span>
          <span>Brands</span>
          <span>Action</span>
        </div>
        {isLoading ? (
          <div className="p-6 text-sm text-neutral-600">Loading outlets...</div>
        ) : outlets.length === 0 ? (
          <div className="p-6 text-sm text-neutral-600">No outlets found.</div>
        ) : (
          outlets.map((outlet) => (
            <div key={outlet.id} className="grid gap-3 border-b border-neutral-100 px-4 py-4 last:border-0 md:grid-cols-[1.4fr_1fr_1fr_1fr_120px] md:items-center">
              <div>
                <Link to={`/outlets/${outlet.id}`} className="font-semibold text-neutral-900 hover:text-primary-600 dark:text-neutral-50">{outlet.shop_name}</Link>
                <p className="text-xs text-neutral-500">{outlet.outlet_id} · {typeLabels[outlet.business_type]}</p>
              </div>
              <div className="text-sm text-neutral-700 dark:text-neutral-300">
                {outlet.owner_name}
                <a href={`tel:${outlet.phone_number}`} className="mt-1 flex items-center gap-1 text-xs text-primary-600"><Phone className="h-3 w-3" /> {outlet.phone_number}</a>
              </div>
              <div className="flex items-center gap-1 text-sm text-neutral-700 dark:text-neutral-300">
                <MapPin className="h-4 w-4 text-neutral-400" />
                {outlet.territory}
              </div>
              <div className="flex flex-wrap gap-1">
                {outlet.brands.map((brand) => <span key={brand} className="rounded bg-gold-100 px-2 py-1 text-xs font-medium text-neutral-900">{brand}</span>)}
              </div>
              <Link to={`/outlets/${outlet.id}`} className="inline-flex h-9 items-center justify-center gap-2 rounded-lg border border-neutral-200 text-sm font-medium">
                <Eye className="h-4 w-4" />
                View
              </Link>
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
    </div>
  )
}
