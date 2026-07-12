import { LocateFixed, Save } from 'lucide-react'
import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { outletService } from '@/services/outlet.service'
import type { BusinessType, OutletBrand, OutletContact, OutletPayload, OutletStatus } from '@/types'

const businessTypes: Array<{ value: BusinessType; label: string }> = [
  { value: 'tea_shop', label: 'Tea Shop' },
  { value: 'cafe', label: 'Cafe' },
  { value: 'bakery', label: 'Bakery' },
  { value: 'restaurant', label: 'Restaurant' },
  { value: 'hotel', label: 'Hotel' },
  { value: 'supermarket', label: 'Supermarket' },
  { value: 'general_store', label: 'General Store' },
]

const emptyForm: OutletPayload = {
  shop_name: '',
  owner_name: '',
  phone_number: '',
  whatsapp_number: '',
  email: '',
  gst_number: '',
  address: '',
  area: '',
  city: 'Chennai',
  district: 'Chennai',
  state: 'Tamil Nadu',
  pincode: '',
  territory: '',
  latitude: null,
  longitude: null,
  google_maps_url: '',
  business_type: 'tea_shop',
  brands: ['TASTIQ'],
  assigned_distributor_id: null,
  status: 'active',
  notes: '',
  contacts: [],
}

export function OutletFormPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const isEdit = Boolean(id)
  const [form, setForm] = useState<OutletPayload>(emptyForm)
  const [isLoading, setIsLoading] = useState(isEdit)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    void outletService.get(id).then((response) => {
      if (response.data) {
        const outlet = response.data
        setForm({
          shop_name: outlet.shop_name,
          owner_name: outlet.owner_name,
          phone_number: outlet.phone_number,
          whatsapp_number: outlet.whatsapp_number ?? '',
          email: outlet.email ?? '',
          gst_number: outlet.gst_number ?? '',
          address: outlet.address,
          area: outlet.area,
          city: outlet.city,
          district: outlet.district,
          state: outlet.state,
          pincode: outlet.pincode,
          territory: outlet.territory,
          latitude: outlet.latitude,
          longitude: outlet.longitude,
          google_maps_url: outlet.google_maps_url ?? '',
          business_type: outlet.business_type,
          brands: outlet.brands,
          assigned_distributor_id: outlet.assigned_distributor_id ?? null,
          status: outlet.status,
          notes: outlet.notes ?? '',
          contacts: outlet.contacts.map(({ name, role, phone, whatsapp, email }): Omit<OutletContact, 'id'> => ({
            name,
            role,
            phone,
            whatsapp,
            email,
          })),
        })
      }
    }).finally(() => setIsLoading(false))
  }, [id])

  const mapsUrl = useMemo(() => {
    if (form.latitude == null || form.longitude == null) return ''
    return `https://www.google.com/maps/search/?api=1&query=${form.latitude},${form.longitude}`
  }, [form.latitude, form.longitude])

  const update = <K extends keyof OutletPayload>(key: K, value: OutletPayload[K]) => {
    setForm((current) => ({ ...current, [key]: value }))
  }

  const toggleBrand = (brand: OutletBrand) => {
    setForm((current) => {
      const brands = current.brands.includes(brand)
        ? current.brands.filter((item) => item !== brand)
        : [...current.brands, brand]
      return { ...current, brands: brands.length ? brands : [brand] }
    })
  }

  const captureGps = () => {
    if (!navigator.geolocation) {
      setError('GPS is not available in this browser.')
      return
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setForm((current) => ({
          ...current,
          latitude: Number(position.coords.latitude.toFixed(6)),
          longitude: Number(position.coords.longitude.toFixed(6)),
          google_maps_url: `https://www.google.com/maps/search/?api=1&query=${position.coords.latitude},${position.coords.longitude}`,
        }))
      },
      () => setError('Unable to capture current GPS location.'),
    )
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setIsSaving(true)
    setError(null)
    try {
      const payload = { ...form, google_maps_url: form.google_maps_url || mapsUrl || null }
      const response = id ? await outletService.update(id, payload) : await outletService.create(payload)
      if (!response.data) throw new Error(response.message)
      navigate(`/outlets/${response.data.id}`, { replace: true })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to save outlet.')
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm">Loading outlet...</div>
  }

  return (
    <form onSubmit={(event) => void submit(event)} className="space-y-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">
            {isEdit ? 'Edit Outlet' : 'Add Outlet'}
          </h2>
          <p className="text-sm text-neutral-600 dark:text-neutral-400">Capture outlet identity, assignment, brands, and GPS.</p>
        </div>
        <button type="submit" disabled={isSaving} className="inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-60">
          <Save className="h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save Outlet'}
        </button>
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}

      <div className="grid grid-cols-1 gap-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark md:grid-cols-2">
        <Input label="Shop Name" value={form.shop_name} onChange={(value) => update('shop_name', value)} required />
        <Input label="Owner Name" value={form.owner_name} onChange={(value) => update('owner_name', value)} required />
        <Input label="Phone Number" value={form.phone_number} onChange={(value) => update('phone_number', value)} required />
        <Input label="WhatsApp Number" value={form.whatsapp_number ?? ''} onChange={(value) => update('whatsapp_number', value)} />
        <Input label="Email" type="email" value={form.email ?? ''} onChange={(value) => update('email', value)} />
        <Input label="GST Number" value={form.gst_number ?? ''} onChange={(value) => update('gst_number', value)} />
        <label className="md:col-span-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Address
          <textarea required value={form.address} onChange={(event) => update('address', event.target.value)} className="mt-1.5 min-h-24 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
        </label>
        <Input label="Area" value={form.area} onChange={(value) => update('area', value)} required />
        <Input label="City" value={form.city} onChange={(value) => update('city', value)} required />
        <Input label="District" value={form.district} onChange={(value) => update('district', value)} required />
        <Input label="State" value={form.state} onChange={(value) => update('state', value)} required />
        <Input label="Pincode" value={form.pincode} onChange={(value) => update('pincode', value)} required />
        <Input label="Territory" value={form.territory} onChange={(value) => update('territory', value)} required />
        <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Business Type
          <select value={form.business_type} onChange={(event) => update('business_type', event.target.value as BusinessType)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
            {businessTypes.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </label>
        <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Status
          <select value={form.status} onChange={(event) => update('status', event.target.value as OutletStatus)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900">
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="blocked">Blocked</option>
          </select>
        </label>
        <div className="md:col-span-2">
          <p className="text-sm font-medium text-neutral-700 dark:text-neutral-300">Brands</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {(['TASTIQ', 'LEMURIA'] as OutletBrand[]).map((brand) => (
              <button key={brand} type="button" onClick={() => toggleBrand(brand)} className={`rounded-lg border px-3 py-1.5 text-sm ${form.brands.includes(brand) ? 'border-primary-600 bg-primary-50 text-primary-600' : 'border-neutral-200 text-neutral-600'}`}>
                {brand}
              </button>
            ))}
          </div>
        </div>
        <Input label="Latitude" type="number" value={form.latitude ?? ''} onChange={(value) => update('latitude', value === '' ? null : Number(value))} />
        <Input label="Longitude" type="number" value={form.longitude ?? ''} onChange={(value) => update('longitude', value === '' ? null : Number(value))} />
        <div className="md:col-span-2 flex flex-col gap-2 sm:flex-row">
          <button type="button" onClick={captureGps} className="inline-flex h-10 items-center justify-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-medium">
            <LocateFixed className="h-4 w-4" />
            Current GPS
          </button>
          {mapsUrl && <a href={mapsUrl} target="_blank" rel="noreferrer" className="inline-flex h-10 items-center justify-center rounded-lg bg-gold-500 px-4 text-sm font-medium text-neutral-900">Open Google Maps</a>}
        </div>
        <label className="md:col-span-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">
          Notes
          <textarea value={form.notes ?? ''} onChange={(event) => update('notes', event.target.value)} className="mt-1.5 min-h-24 w-full rounded-lg border border-neutral-200 bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
        </label>
      </div>
    </form>
  )
}

interface InputProps {
  label: string
  value: string | number
  onChange: (value: string) => void
  type?: string
  required?: boolean
}

function Input({ label, value, onChange, type = 'text', required = false }: InputProps) {
  return (
    <label className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
      {label}
      <input required={required} type={type} value={value} onChange={(event) => onChange(event.target.value)} className="mt-1.5 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
    </label>
  )
}
