import { AlertTriangle, Package, Plus, Search } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { productService } from '@/services/product.service'
import type { Product } from '@/types'

const brandLabels: Record<string, string> = {
  TASTIQ: 'TASTIQ',
  LEMURIA: 'LEMURIA',
}

const statusStyles: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-neutral-200 text-neutral-700',
  discontinued: 'bg-red-100 text-red-800',
}

export function ProductListPage() {
  const [searchParams] = useSearchParams()
  const [products, setProducts] = useState<Product[]>([])
  const [search, setSearch] = useState('')
  const [brand, setBrand] = useState('')
  const [status, setStatus] = useState('')
  const [lowStockOnly, setLowStockOnly] = useState(searchParams.get('low_stock_only') === 'true')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    setIsLoading(true)
    void productService
      .list({
        page,
        page_size: 10,
        search: search || undefined,
        brand: brand || undefined,
        status: status || undefined,
        low_stock_only: lowStockOnly || undefined,
      })
      .then((response) => {
        setProducts(response.data ?? [])
        setTotalPages(response.total_pages)
      })
      .finally(() => setIsLoading(false))
  }, [page, search, brand, status, lowStockOnly])

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Product Catalog</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Manage SKUs, pricing, and stock across TASTIQ and LEMURIA.</p>
        </div>
        <Link to="/products/new" className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700">
          <Plus className="h-4 w-4" />
          Add Product
        </Link>
      </div>

      <div className="grid gap-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark md:grid-cols-[1fr_160px_160px_auto]">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-neutral-400" />
          <input
            value={search}
            onChange={(event) => { setSearch(event.target.value); setPage(1) }}
            placeholder="Search SKU, name, barcode"
            className="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-10 pr-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
        </div>
        <select value={brand} onChange={(event) => { setBrand(event.target.value); setPage(1) }} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
          <option value="">All Brands</option>
          {Object.entries(brandLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
        </select>
        <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1) }} className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
          <option value="discontinued">Discontinued</option>
        </select>
        <label className="flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700">
          <input type="checkbox" checked={lowStockOnly} onChange={(event) => { setLowStockOnly(event.target.checked); setPage(1) }} />
          Low stock only
        </label>
      </div>

      <div className="overflow-hidden rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        <div className="hidden grid-cols-[1.4fr_1fr_1fr_1fr_120px] gap-4 border-b border-neutral-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-neutral-500 md:grid">
          <span>Product</span>
          <span>Category</span>
          <span>Price (MRP / Dist.)</span>
          <span>Stock</span>
          <span>Status</span>
        </div>
        {isLoading ? (
          <div className="p-6 text-sm text-neutral-600">Loading products...</div>
        ) : products.length === 0 ? (
          <div className="p-6 text-sm text-neutral-600">No products found.</div>
        ) : (
          products.map((product) => (
            <div key={product.id} className="grid gap-3 border-b border-neutral-100 px-4 py-4 last:border-0 md:grid-cols-[1.4fr_1fr_1fr_1fr_120px] md:items-center">
              <div>
                <Link to={`/products/${product.id}/edit`} className="font-semibold text-neutral-900 hover:text-primary-600 dark:text-neutral-50">
                  {product.name}
                </Link>
                <p className="text-xs text-neutral-500">{product.sku} · {brandLabels[product.brand]}</p>
              </div>
              <div className="flex items-center gap-1 text-sm text-neutral-700 dark:text-neutral-300">
                <Package className="h-4 w-4 text-neutral-400" />
                {product.category?.name ?? 'Uncategorized'}
              </div>
              <div className="text-sm text-neutral-700 dark:text-neutral-300">
                ₹{product.mrp} / ₹{product.distributor_price}
              </div>
              <div className="flex items-center gap-1 text-sm text-neutral-700 dark:text-neutral-300">
                {product.is_low_stock && <AlertTriangle className="h-4 w-4 text-amber-500" />}
                {product.stock_quantity} {product.unit}
              </div>
              <span className={`inline-flex w-fit items-center rounded px-2 py-1 text-xs font-medium capitalize ${statusStyles[product.status]}`}>
                {product.status}
              </span>
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
