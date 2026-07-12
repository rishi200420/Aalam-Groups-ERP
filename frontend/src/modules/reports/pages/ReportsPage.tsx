import { Download, FileBarChart } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { inventoryService } from '@/services/inventory.service'
import { reportsService } from '@/services/reports.service'
import type {
  DeadStockReport,
  DispatchReport,
  InventoryReport,
  LowStockReport,
  OrderReport,
  OutletReport,
  ReportType,
  SalesReport,
  StockMovementReport,
  TopSellingReport,
  Warehouse,
  WarehouseReport,
} from '@/types'

const REPORT_TABS: { value: ReportType; label: string }[] = [
  { value: 'sales', label: 'Sales' },
  { value: 'inventory', label: 'Inventory' },
  { value: 'stock-movements', label: 'Stock Movement' },
  { value: 'dispatch', label: 'Dispatch' },
  { value: 'orders', label: 'Orders' },
  { value: 'outlets', label: 'Outlet' },
  { value: 'warehouses', label: 'Warehouse' },
  { value: 'top-selling', label: 'Top Selling' },
  { value: 'low-stock', label: 'Low Stock' },
  { value: 'dead-stock', label: 'Dead Stock' },
]

const USES_DATE_RANGE: ReportType[] = ['sales', 'stock-movements', 'dispatch', 'orders', 'outlets', 'top-selling']
const USES_WAREHOUSE_FILTER: ReportType[] = ['inventory', 'stock-movements', 'low-stock']
const USES_STATUS_FILTER: ReportType[] = ['dispatch', 'orders']

function todayIso(): string {
  return new Date().toISOString().slice(0, 10)
}

function daysAgoIso(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() - days)
  return d.toISOString().slice(0, 10)
}

function currency(value: string | number): string {
  return `₹${Number(value || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
}

export function ReportsPage() {
  const [activeReport, setActiveReport] = useState<ReportType>('sales')
  const [startDate, setStartDate] = useState(daysAgoIso(29))
  const [endDate, setEndDate] = useState(todayIso())
  const [warehouseId, setWarehouseId] = useState('')
  const [status, setStatus] = useState('')
  const [thresholdDays, setThresholdDays] = useState(60)
  const [warehouses, setWarehouses] = useState<Warehouse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState('')

  const [sales, setSales] = useState<SalesReport | null>(null)
  const [inventory, setInventory] = useState<InventoryReport | null>(null)
  const [stockMovements, setStockMovements] = useState<StockMovementReport | null>(null)
  const [dispatch, setDispatch] = useState<DispatchReport | null>(null)
  const [orders, setOrders] = useState<OrderReport | null>(null)
  const [outlets, setOutlets] = useState<OutletReport | null>(null)
  const [warehouseReport, setWarehouseReport] = useState<WarehouseReport | null>(null)
  const [topSelling, setTopSelling] = useState<TopSellingReport | null>(null)
  const [lowStock, setLowStock] = useState<LowStockReport | null>(null)
  const [deadStock, setDeadStock] = useState<DeadStockReport | null>(null)

  useEffect(() => {
    void inventoryService.listWarehouses().then((response) => setWarehouses(response.data ?? []))
  }, [])

  const filters = useMemo(
    () => ({
      start_date: USES_DATE_RANGE.includes(activeReport) ? startDate : undefined,
      end_date: USES_DATE_RANGE.includes(activeReport) ? endDate : undefined,
      warehouse_id: USES_WAREHOUSE_FILTER.includes(activeReport) ? warehouseId || undefined : undefined,
      status: USES_STATUS_FILTER.includes(activeReport) ? status || undefined : undefined,
      threshold_days: activeReport === 'dead-stock' ? thresholdDays : undefined,
    }),
    [activeReport, startDate, endDate, warehouseId, status, thresholdDays],
  )

  useEffect(() => {
    const load = async () => {
      setIsLoading(true)
      setError('')
      try {
        switch (activeReport) {
          case 'sales':
            setSales((await reportsService.sales(filters)).data ?? null)
            break
          case 'inventory':
            setInventory((await reportsService.inventory(filters)).data ?? null)
            break
          case 'stock-movements':
            setStockMovements((await reportsService.stockMovements(filters)).data ?? null)
            break
          case 'dispatch':
            setDispatch((await reportsService.dispatch(filters)).data ?? null)
            break
          case 'orders':
            setOrders((await reportsService.orders(filters)).data ?? null)
            break
          case 'outlets':
            setOutlets((await reportsService.outlets(filters)).data ?? null)
            break
          case 'warehouses':
            setWarehouseReport((await reportsService.warehouses()).data ?? null)
            break
          case 'top-selling':
            setTopSelling((await reportsService.topSelling(filters)).data ?? null)
            break
          case 'low-stock':
            setLowStock((await reportsService.lowStock(filters)).data ?? null)
            break
          case 'dead-stock':
            setDeadStock((await reportsService.deadStock(filters)).data ?? null)
            break
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load report')
      } finally {
        setIsLoading(false)
      }
    }
    void load()
  }, [activeReport, filters])

  const handleExport = async () => {
    setIsExporting(true)
    try {
      await reportsService.exportCsv(activeReport, filters)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export report')
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Reports</h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Sales, inventory, dispatch, and outlet performance analytics.</p>
        </div>
        <button
          type="button"
          onClick={handleExport}
          disabled={isExporting}
          className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-60"
        >
          <Download className="h-4 w-4" />
          {isExporting ? 'Exporting...' : 'Export CSV'}
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {REPORT_TABS.map((tab) => (
          <button
            key={tab.value}
            type="button"
            onClick={() => setActiveReport(tab.value)}
            className={`h-9 rounded-full border px-4 text-sm font-semibold transition ${
              activeReport === tab.value
                ? 'border-primary-600 bg-primary-50 text-primary-700 dark:bg-primary-900/30'
                : 'border-neutral-200 text-neutral-600 hover:bg-neutral-50 dark:border-neutral-700 dark:text-neutral-300'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex flex-wrap items-end gap-3 rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark">
        {USES_DATE_RANGE.includes(activeReport) && (
          <>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">From</label>
              <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="mt-1 h-9 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">To</label>
              <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="mt-1 h-9 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
            </div>
          </>
        )}
        {USES_WAREHOUSE_FILTER.includes(activeReport) && (
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Warehouse</label>
            <select value={warehouseId} onChange={(e) => setWarehouseId(e.target.value)} className="mt-1 h-9 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
              <option value="">All Warehouses</option>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
          </div>
        )}
        {USES_STATUS_FILTER.includes(activeReport) && (
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Status</label>
            <input value={status} onChange={(e) => setStatus(e.target.value)} placeholder="e.g. delivered" className="mt-1 h-9 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
          </div>
        )}
        {activeReport === 'dead-stock' && (
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">No movement for (days)</label>
            <input type="number" min={1} value={thresholdDays} onChange={(e) => setThresholdDays(Number(e.target.value))} className="mt-1 h-9 w-32 rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
          </div>
        )}
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      {isLoading ? (
        <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-600 dark:border-neutral-800 dark:bg-surface-dark">Loading report...</div>
      ) : (
        <div className="space-y-4">
          {activeReport === 'sales' && sales && <SalesReportView data={sales} />}
          {activeReport === 'inventory' && inventory && <InventoryReportView data={inventory} />}
          {activeReport === 'stock-movements' && stockMovements && <StockMovementReportView data={stockMovements} />}
          {activeReport === 'dispatch' && dispatch && <DispatchReportView data={dispatch} />}
          {activeReport === 'orders' && orders && <OrderReportView data={orders} />}
          {activeReport === 'outlets' && outlets && <OutletReportView data={outlets} />}
          {activeReport === 'warehouses' && warehouseReport && <WarehouseReportView data={warehouseReport} />}
          {activeReport === 'top-selling' && topSelling && <TopSellingReportView data={topSelling} />}
          {activeReport === 'low-stock' && lowStock && <LowStockReportView data={lowStock} />}
          {activeReport === 'dead-stock' && deadStock && <DeadStockReportView data={deadStock} />}
        </div>
      )}
    </div>
  )
}

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 dark:border-neutral-800 dark:bg-surface-dark">
      <p className="text-xs font-semibold uppercase tracking-wide text-neutral-500">{label}</p>
      <p className="mt-1 text-xl font-semibold text-neutral-900 dark:text-neutral-50">{value}</p>
    </div>
  )
}

function Table({ headers, children }: { headers: string[]; children: React.ReactNode }) {
  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white dark:border-neutral-800 dark:bg-surface-dark">
      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-neutral-200 text-xs font-semibold uppercase tracking-wide text-neutral-500 dark:border-neutral-800">
            {headers.map((h) => (
              <th key={h} className="px-4 py-3">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">{children}</tbody>
      </table>
    </div>
  )
}

function EmptyRow({ colSpan }: { colSpan: number }) {
  return (
    <tr>
      <td colSpan={colSpan} className="px-4 py-6 text-center text-sm text-neutral-500">No data for this range.</td>
    </tr>
  )
}

function SalesReportView({ data }: { data: SalesReport }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-3">
        <Card label="Total Orders" value={data.total_orders} />
        <Card label="Total Revenue" value={currency(data.total_revenue)} />
        <Card label="Avg Order Value" value={currency(data.average_order_value)} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Table headers={['Status', 'Orders']}>
          {data.by_status.length === 0 ? <EmptyRow colSpan={2} /> : data.by_status.map((s) => (
            <tr key={s.status}><td className="px-4 py-2 capitalize">{s.status}</td><td className="px-4 py-2">{s.count}</td></tr>
          ))}
        </Table>
        <Table headers={['Brand', 'Orders', 'Revenue']}>
          {data.by_brand.length === 0 ? <EmptyRow colSpan={3} /> : data.by_brand.map((b) => (
            <tr key={b.brand}><td className="px-4 py-2">{b.brand}</td><td className="px-4 py-2">{b.orders_count}</td><td className="px-4 py-2">{currency(b.revenue)}</td></tr>
          ))}
        </Table>
      </div>
      <Table headers={['Date', 'Orders', 'Revenue']}>
        {data.daily.map((d) => (
          <tr key={d.date}><td className="px-4 py-2">{d.date}</td><td className="px-4 py-2">{d.orders_count}</td><td className="px-4 py-2">{currency(d.revenue)}</td></tr>
        ))}
      </Table>
    </div>
  )
}

function InventoryReportView({ data }: { data: InventoryReport }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-4">
        <Card label="Total Items" value={data.total_items} />
        <Card label="Inventory Value" value={currency(data.total_value)} />
        <Card label="Low Stock" value={data.low_stock_count} />
        <Card label="Out of Stock" value={data.out_of_stock_count} />
      </div>
      <Table headers={['Product', 'SKU', 'Warehouse', 'Stock', 'Value', 'Status']}>
        {data.rows.length === 0 ? <EmptyRow colSpan={6} /> : data.rows.map((r, i) => (
          <tr key={`${r.sku}-${i}`}>
            <td className="px-4 py-2">{r.product_name}</td>
            <td className="px-4 py-2">{r.sku}</td>
            <td className="px-4 py-2">{r.warehouse_name}</td>
            <td className="px-4 py-2">{r.current_stock}</td>
            <td className="px-4 py-2">{currency(r.inventory_value)}</td>
            <td className="px-4 py-2 capitalize">{r.status.replace('_', ' ')}</td>
          </tr>
        ))}
      </Table>
    </div>
  )
}

function StockMovementReportView({ data }: { data: StockMovementReport }) {
  return (
    <div className="space-y-4">
      <Card label="Total Movements" value={data.total_movements} />
      <Table headers={['Date', 'Product', 'Warehouse', 'Type', 'Quantity', 'Notes']}>
        {data.rows.length === 0 ? <EmptyRow colSpan={6} /> : data.rows.map((r, i) => (
          <tr key={i}>
            <td className="px-4 py-2">{new Date(r.date).toLocaleString()}</td>
            <td className="px-4 py-2">{r.product_name}</td>
            <td className="px-4 py-2">{r.warehouse_name}</td>
            <td className="px-4 py-2 capitalize">{r.movement_type.replace('_', ' ')}</td>
            <td className={`px-4 py-2 font-medium ${r.quantity >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>{r.quantity > 0 ? '+' : ''}{r.quantity}</td>
            <td className="px-4 py-2 text-neutral-500">{r.notes || '—'}</td>
          </tr>
        ))}
      </Table>
    </div>
  )
}

function DispatchReportView({ data }: { data: DispatchReport }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <Card label="Total Dispatches" value={data.total_dispatches} />
        <Card label="Avg Delivery Time" value={data.average_delivery_hours ? `${data.average_delivery_hours} hrs` : '—'} />
      </div>
      <Table headers={['Dispatch #', 'Order #', 'Outlet', 'Status', 'Delivered', 'Hours']}>
        {data.rows.length === 0 ? <EmptyRow colSpan={6} /> : data.rows.map((r) => (
          <tr key={r.dispatch_number}>
            <td className="px-4 py-2">{r.dispatch_number}</td>
            <td className="px-4 py-2">{r.order_number}</td>
            <td className="px-4 py-2">{r.outlet_name}</td>
            <td className="px-4 py-2 capitalize">{r.status.replace('_', ' ')}</td>
            <td className="px-4 py-2">{r.delivered_at ? new Date(r.delivered_at).toLocaleString() : '—'}</td>
            <td className="px-4 py-2">{r.delivery_hours ?? '—'}</td>
          </tr>
        ))}
      </Table>
    </div>
  )
}

function OrderReportView({ data }: { data: OrderReport }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-2">
        <Card label="Total Orders" value={data.total_orders} />
        <Card label="Total Revenue" value={currency(data.total_revenue)} />
      </div>
      <Table headers={['Order #', 'Outlet', 'Status', 'Amount', 'Date']}>
        {data.rows.length === 0 ? <EmptyRow colSpan={5} /> : data.rows.map((r) => (
          <tr key={r.order_number}>
            <td className="px-4 py-2">{r.order_number}</td>
            <td className="px-4 py-2">{r.outlet_name}</td>
            <td className="px-4 py-2 capitalize">{r.status}</td>
            <td className="px-4 py-2">{currency(r.total_amount)}</td>
            <td className="px-4 py-2">{new Date(r.created_at).toLocaleDateString()}</td>
          </tr>
        ))}
      </Table>
    </div>
  )
}

function OutletReportView({ data }: { data: OutletReport }) {
  return (
    <Table headers={['Outlet', 'Territory', 'Orders', 'Revenue', 'Last Order']}>
      {data.rows.length === 0 ? <EmptyRow colSpan={5} /> : data.rows.map((r) => (
        <tr key={r.outlet_id}>
          <td className="px-4 py-2">{r.outlet_name}</td>
          <td className="px-4 py-2">{r.territory}</td>
          <td className="px-4 py-2">{r.orders_count}</td>
          <td className="px-4 py-2">{currency(r.revenue)}</td>
          <td className="px-4 py-2">{r.last_order_at ? new Date(r.last_order_at).toLocaleDateString() : '—'}</td>
        </tr>
      ))}
    </Table>
  )
}

function WarehouseReportView({ data }: { data: WarehouseReport }) {
  return (
    <Table headers={['Warehouse', 'Code', 'Items', 'Value', 'Low Stock', 'Out of Stock']}>
      {data.rows.length === 0 ? <EmptyRow colSpan={6} /> : data.rows.map((r) => (
        <tr key={r.warehouse_code}>
          <td className="px-4 py-2">{r.warehouse_name}</td>
          <td className="px-4 py-2">{r.warehouse_code}</td>
          <td className="px-4 py-2">{r.total_items}</td>
          <td className="px-4 py-2">{currency(r.total_value)}</td>
          <td className="px-4 py-2">{r.low_stock_count}</td>
          <td className="px-4 py-2">{r.out_of_stock_count}</td>
        </tr>
      ))}
    </Table>
  )
}

function TopSellingReportView({ data }: { data: TopSellingReport }) {
  return (
    <Table headers={['Product', 'SKU', 'Brand', 'Units Sold', 'Revenue']}>
      {data.rows.length === 0 ? <EmptyRow colSpan={5} /> : data.rows.map((r) => (
        <tr key={r.sku}>
          <td className="px-4 py-2">{r.product_name}</td>
          <td className="px-4 py-2">{r.sku}</td>
          <td className="px-4 py-2">{r.brand}</td>
          <td className="px-4 py-2">{r.units_sold}</td>
          <td className="px-4 py-2">{currency(r.revenue)}</td>
        </tr>
      ))}
    </Table>
  )
}

function LowStockReportView({ data }: { data: LowStockReport }) {
  return (
    <Table headers={['Product', 'SKU', 'Warehouse', 'Current', 'Min', 'Reorder Qty', 'Status']}>
      {data.rows.length === 0 ? <EmptyRow colSpan={7} /> : data.rows.map((r, i) => (
        <tr key={`${r.sku}-${i}`}>
          <td className="px-4 py-2">{r.product_name}</td>
          <td className="px-4 py-2">{r.sku}</td>
          <td className="px-4 py-2">{r.warehouse_name}</td>
          <td className="px-4 py-2">{r.current_stock}</td>
          <td className="px-4 py-2">{r.minimum_stock}</td>
          <td className="px-4 py-2 font-medium text-amber-600">{r.reorder_quantity}</td>
          <td className="px-4 py-2 capitalize">{r.status.replace('_', ' ')}</td>
        </tr>
      ))}
    </Table>
  )
}

function DeadStockReportView({ data }: { data: DeadStockReport }) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
        <FileBarChart className="h-4 w-4" />
        Items with no stock movement in the last {data.threshold_days} days.
      </div>
      <Table headers={['Product', 'SKU', 'Warehouse', 'Stock', 'Value', 'Last Movement', 'Days Idle']}>
        {data.rows.length === 0 ? <EmptyRow colSpan={7} /> : data.rows.map((r, i) => (
          <tr key={`${r.sku}-${i}`}>
            <td className="px-4 py-2">{r.product_name}</td>
            <td className="px-4 py-2">{r.sku}</td>
            <td className="px-4 py-2">{r.warehouse_name}</td>
            <td className="px-4 py-2">{r.current_stock}</td>
            <td className="px-4 py-2">{currency(r.inventory_value)}</td>
            <td className="px-4 py-2">{r.last_movement_at ? new Date(r.last_movement_at).toLocaleDateString() : 'Never'}</td>
            <td className="px-4 py-2">{r.days_since_movement ?? '—'}</td>
          </tr>
        ))}
      </Table>
    </div>
  )
}
