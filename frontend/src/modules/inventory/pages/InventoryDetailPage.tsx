import { ArrowLeft, ArrowLeftRight, Boxes, PackagePlus, TrendingDown, Warehouse } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { inventoryService } from '@/services/inventory.service'
import type { Inventory, StockMovement, Warehouse as WarehouseType } from '@/types'

export function InventoryDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [item, setItem] = useState<Inventory | null>(null)
  const [movements, setMovements] = useState<StockMovement[]>([])
  const [warehouses, setWarehouses] = useState<WarehouseType[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')

  const [showAdjust, setShowAdjust] = useState(false)
  const [adjustQuantity, setAdjustQuantity] = useState(0)
  const [adjustReason, setAdjustReason] = useState('')
  const [isAdjusting, setIsAdjusting] = useState(false)

  const [showTransfer, setShowTransfer] = useState(false)
  const [transferWarehouseId, setTransferWarehouseId] = useState('')
  const [transferQuantity, setTransferQuantity] = useState(0)
  const [transferNotes, setTransferNotes] = useState('')
  const [isTransferring, setIsTransferring] = useState(false)

  const loadData = async () => {
    if (!id) return
    setIsLoading(true)
    try {
      const [itemResponse, movementResponse] = await Promise.all([
        inventoryService.get(id),
        inventoryService.listMovements({ inventory_id: id, page: 1, page_size: 10 }),
      ])
      if (itemResponse.success) {
        setItem(itemResponse.data)
      } else {
        setError(itemResponse.message)
      }
      setMovements(movementResponse.data ?? [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load inventory item')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void loadData()
    void inventoryService.listWarehouses().then((response) => setWarehouses(response.data ?? []))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id])

  const submitAdjust = async (event: FormEvent) => {
    event.preventDefault()
    if (!id || adjustQuantity === 0 || !adjustReason.trim()) {
      setActionError('Enter a non-zero quantity and a reason.')
      return
    }
    setIsAdjusting(true)
    setActionError('')
    try {
      await inventoryService.adjust(id, { quantity: adjustQuantity, reason: adjustReason })
      setShowAdjust(false)
      setAdjustQuantity(0)
      setAdjustReason('')
      await loadData()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Unable to adjust stock.')
    } finally {
      setIsAdjusting(false)
    }
  }

  const submitTransfer = async (event: FormEvent) => {
    event.preventDefault()
    if (!id || !transferWarehouseId || transferQuantity <= 0) {
      setActionError('Select a target warehouse and a positive quantity.')
      return
    }
    setIsTransferring(true)
    setActionError('')
    try {
      await inventoryService.transfer(id, {
        target_warehouse_id: transferWarehouseId,
        quantity: transferQuantity,
        notes: transferNotes || undefined,
      })
      setShowTransfer(false)
      setTransferWarehouseId('')
      setTransferQuantity(0)
      setTransferNotes('')
      await loadData()
    } catch (err) {
      setActionError(err instanceof Error ? err.message : 'Unable to transfer stock.')
    } finally {
      setIsTransferring(false)
    }
  }

  if (isLoading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-600 dark:border-neutral-800 dark:bg-surface-dark dark:text-neutral-400">Loading inventory item...</div>
  }

  if (error || !item) {
    return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-700">{error || 'Inventory item not found'}</div>
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <Link to="/inventory" className="inline-flex items-center gap-2 text-sm font-medium text-primary-600 hover:text-primary-700">
            <ArrowLeft className="h-4 w-4" />
            Back to inventory
          </Link>
          <h2 className="mt-2 text-2xl font-semibold text-neutral-900 dark:text-neutral-50">{item.product_name || item.sku}</h2>
          <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">{item.sku} · {item.warehouse_name}</p>
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => {
              setShowAdjust((value) => !value)
              setShowTransfer(false)
              setActionError('')
            }}
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-medium text-neutral-700 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300"
          >
            <PackagePlus className="h-4 w-4" />
            Adjust Stock
          </button>
          <button
            type="button"
            onClick={() => {
              setShowTransfer((value) => !value)
              setShowAdjust(false)
              setActionError('')
            }}
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700"
          >
            <ArrowLeftRight className="h-4 w-4" />
            Transfer Stock
          </button>
        </div>
      </div>

      {actionError && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{actionError}</div>}

      {showAdjust && (
        <form onSubmit={submitAdjust} className="space-y-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark">
          <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-50">Adjust stock</p>
          <div className="grid gap-3 sm:grid-cols-[160px_1fr]">
            <input
              type="number"
              placeholder="Quantity (+/-)"
              value={adjustQuantity}
              onChange={(event) => setAdjustQuantity(Number(event.target.value))}
              className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
            <input
              placeholder="Reason (e.g. damaged goods, stock count correction)"
              value={adjustReason}
              onChange={(event) => setAdjustReason(event.target.value)}
              className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <p className="text-xs text-neutral-500">Use a positive number to add stock (e.g. purchase) or a negative number to remove stock (e.g. damage).</p>
          <button type="submit" disabled={isAdjusting} className="h-9 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-60">
            {isAdjusting ? 'Saving...' : 'Save adjustment'}
          </button>
        </form>
      )}

      {showTransfer && (
        <form onSubmit={submitTransfer} className="space-y-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark">
          <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-50">Transfer stock to another warehouse</p>
          <div className="grid gap-3 sm:grid-cols-[1fr_140px]">
            <select
              value={transferWarehouseId}
              onChange={(event) => setTransferWarehouseId(event.target.value)}
              className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            >
              <option value="">Select target warehouse</option>
              {warehouses
                .filter((warehouse) => warehouse.id !== item.warehouse_id)
                .map((warehouse) => (
                  <option key={warehouse.id} value={warehouse.id}>
                    {warehouse.name} ({warehouse.code})
                  </option>
                ))}
            </select>
            <input
              type="number"
              min={1}
              placeholder="Quantity"
              value={transferQuantity}
              onChange={(event) => setTransferQuantity(Number(event.target.value))}
              className="h-10 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <input
            placeholder="Notes (optional)"
            value={transferNotes}
            onChange={(event) => setTransferNotes(event.target.value)}
            className="h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
          />
          <p className="text-xs text-neutral-500">Available for transfer: {item.available_stock} units.</p>
          <button type="submit" disabled={isTransferring} className="h-9 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-60">
            {isTransferring ? 'Transferring...' : 'Confirm transfer'}
          </button>
        </form>
      )}

      <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
          <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-neutral-500">
            <Boxes className="h-4 w-4" />
            Stock Summary
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-neutral-200 p-4">
              <p className="text-xs uppercase tracking-wide text-neutral-500">Available</p>
              <p className="mt-1 text-xl font-semibold text-neutral-900">{item.available_stock}</p>
            </div>
            <div className="rounded-lg border border-neutral-200 p-4">
              <p className="text-xs uppercase tracking-wide text-neutral-500">Reserved</p>
              <p className="mt-1 text-xl font-semibold text-neutral-900">{item.reserved_stock}</p>
            </div>
            <div className="rounded-lg border border-neutral-200 p-4">
              <p className="text-xs uppercase tracking-wide text-neutral-500">Dispatched</p>
              <p className="mt-1 text-xl font-semibold text-neutral-900">{item.dispatched_stock}</p>
            </div>
          </div>
          <div className="mt-4 rounded-lg border border-neutral-200 p-4">
            <div className="flex items-center gap-2 text-sm text-neutral-700 dark:text-neutral-300">
              <Warehouse className="h-4 w-4 text-neutral-400" />
              Warehouse: {item.warehouse_name}
            </div>
            <div className="mt-2 flex items-center gap-2 text-sm text-neutral-700 dark:text-neutral-300">
              <TrendingDown className="h-4 w-4 text-neutral-400" />
              Current stock: {item.current_stock} (min {item.minimum_stock} / max {item.maximum_stock})
            </div>
            {item.reorder_quantity > 0 && (
              <div className="mt-2 rounded-md bg-amber-50 px-3 py-2 text-xs font-medium text-amber-700">
                Recommended reorder: {item.reorder_quantity} units
              </div>
            )}
          </div>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
          <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">Inventory Value</h3>
          <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">Purchase cost and current valuation.</p>
          <div className="mt-4 space-y-3 text-sm text-neutral-700 dark:text-neutral-300">
            <div className="flex items-center justify-between"><span>Purchase cost</span><span>₹{Number(item.purchase_cost || 0).toLocaleString('en-IN')}</span></div>
            <div className="flex items-center justify-between"><span>Selling price</span><span>₹{Number(item.selling_price || 0).toLocaleString('en-IN')}</span></div>
            <div className="flex items-center justify-between font-semibold text-neutral-900 dark:text-neutral-50"><span>Inventory value</span><span>₹{Number(item.inventory_value || 0).toLocaleString('en-IN')}</span></div>
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
        <div className="border-b border-neutral-200 px-4 py-3 text-sm font-semibold text-neutral-900 dark:border-neutral-800 dark:text-neutral-50">Recent Stock Movements</div>
        {movements.length === 0 ? (
          <div className="p-4 text-sm text-neutral-600">No stock movements recorded.</div>
        ) : (
          <div className="divide-y divide-neutral-100 dark:divide-neutral-800">
            {movements.map((movement) => (
              <div key={movement.id} className="flex items-center justify-between px-4 py-3 text-sm text-neutral-700 dark:text-neutral-300">
                <div>
                  <p className="font-medium capitalize text-neutral-900 dark:text-neutral-50">{movement.movement_type.replace('_', ' ')}</p>
                  <p className="text-xs text-neutral-500">{movement.notes || 'No notes'}</p>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${movement.quantity >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>{movement.quantity > 0 ? '+' : ''}{movement.quantity}</p>
                  <p className="text-xs text-neutral-500">{new Date(movement.created_at).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
