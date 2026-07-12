import { CalendarPlus, Camera, Edit, MapPinned, MessageCircle, Navigation, Phone, ShoppingCart, Trash2 } from 'lucide-react'
import { useEffect, useMemo, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { outletService } from '@/services/outlet.service'
import type { Outlet } from '@/types'

const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1').replace('/api/v1', '')

export function OutletDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { isFounder } = useAuth()
  const [outlet, setOutlet] = useState<Outlet | null>(null)
  const [notes, setNotes] = useState('')
  const [nextFollowUp, setNextFollowUp] = useState('')
  const [visitError, setVisitError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const load = () => {
    if (!id) return
    setIsLoading(true)
    void outletService.get(id).then((response) => setOutlet(response.data)).finally(() => setIsLoading(false))
  }

  useEffect(load, [id])

  const mapsUrl = useMemo(() => {
    if (!outlet) return ''
    if (outlet.google_maps_url) return outlet.google_maps_url
    if (outlet.latitude == null || outlet.longitude == null) return ''
    return `https://www.google.com/maps/search/?api=1&query=${outlet.latitude},${outlet.longitude}`
  }, [outlet])

  const addVisit = async (event: FormEvent) => {
    event.preventDefault()
    if (!id) return
    setVisitError(null)
    const submit = async (latitude?: number, longitude?: number) => {
      const response = await outletService.addVisit(id, {
        notes,
        next_follow_up_date: nextFollowUp ? new Date(nextFollowUp).toISOString() : undefined,
        latitude,
        longitude,
      })
      if (response.data) {
        setOutlet(response.data)
        setNotes('')
        setNextFollowUp('')
      }
    }

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => void submit(position.coords.latitude, position.coords.longitude),
        () => void submit(),
      )
    } else {
      await submit()
    }
  }

  const uploadPhoto = async (file: File | undefined, photoType: string) => {
    if (!id || !file) return
    const response = await outletService.uploadPhoto(id, photoType, file)
    if (response.data) setOutlet(response.data)
  }

  const deleteOutlet = async () => {
    if (!id) return
    await outletService.remove(id)
    navigate('/outlets', { replace: true })
  }

  if (isLoading) return <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm">Loading outlet...</div>
  if (!outlet) return <div className="rounded-lg border border-neutral-200 bg-white p-5 text-sm">Outlet not found.</div>

  return (
    <div className="space-y-5">
      <div className="flex flex-col gap-3 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">{outlet.shop_name}</h2>
            <span className="rounded-full bg-primary-50 px-2.5 py-1 text-xs font-semibold uppercase text-primary-600">{outlet.status}</span>
          </div>
          <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">
            {outlet.outlet_id} · {outlet.owner_name} · {outlet.area}, {outlet.city}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <a href={`tel:${outlet.phone_number}`} className="inline-flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-3 text-sm font-medium"><Phone className="h-4 w-4" />Call</a>
          <a href={`https://wa.me/${outlet.whatsapp_number ?? outlet.phone_number}`} target="_blank" rel="noreferrer" className="inline-flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-3 text-sm font-medium"><MessageCircle className="h-4 w-4" />WhatsApp</a>
          {mapsUrl && <a href={mapsUrl} target="_blank" rel="noreferrer" className="inline-flex h-10 items-center gap-2 rounded-lg bg-gold-500 px-3 text-sm font-medium text-neutral-900"><Navigation className="h-4 w-4" />Navigate</a>}
          <Link to={`/outlets/${outlet.id}/edit`} className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary-600 px-3 text-sm font-medium text-white"><Edit className="h-4 w-4" />Edit</Link>
          <Link to="/orders" className="inline-flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-3 text-sm font-medium"><ShoppingCart className="h-4 w-4" />Create Order</Link>
          {isFounder && <button type="button" onClick={() => void deleteOutlet()} className="inline-flex h-10 items-center gap-2 rounded-lg border border-red-200 px-3 text-sm font-medium text-red-600"><Trash2 className="h-4 w-4" />Delete</button>}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.4fr_0.6fr]">
        <div className="space-y-5">
          <section className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Outlet Profile</h3>
            <div className="mt-4 grid gap-4 sm:grid-cols-2">
              <Info label="Business Type" value={labelize(outlet.business_type)} />
              <Info label="Territory" value={outlet.territory} />
              <Info label="Phone" value={outlet.phone_number} />
              <Info label="WhatsApp" value={outlet.whatsapp_number ?? '-'} />
              <Info label="GST" value={outlet.gst_number ?? '-'} />
              <Info label="Brands" value={outlet.brands.join(', ')} />
              <Info label="Address" value={`${outlet.address}, ${outlet.district}, ${outlet.state} - ${outlet.pincode}`} wide />
              <Info label="Notes" value={outlet.notes || '-'} wide />
            </div>
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Visit History</h3>
              <CalendarPlus className="h-5 w-5 text-primary-600" />
            </div>
            <form onSubmit={(event) => void addVisit(event)} className="mt-4 grid gap-3 sm:grid-cols-[1fr_180px_auto]">
              <input value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Add visit notes" className="h-10 rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              <input type="date" value={nextFollowUp} onChange={(event) => setNextFollowUp(event.target.value)} className="h-10 rounded-lg border border-neutral-200 px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900" />
              <button type="submit" className="h-10 rounded-lg bg-primary-600 px-4 text-sm font-medium text-white">Add Visit</button>
            </form>
            {visitError && <p className="mt-2 text-sm text-red-600">{visitError}</p>}
            <div className="mt-4 space-y-3">
              {outlet.visits.length === 0 ? <p className="text-sm text-neutral-500">No visits recorded.</p> : outlet.visits.map((visit) => (
                <div key={visit.id} className="rounded-lg bg-neutral-50 p-4 text-sm dark:bg-neutral-800/50">
                  <p className="font-medium text-neutral-900 dark:text-neutral-50">{new Date(visit.visit_date).toLocaleString()}</p>
                  <p className="mt-1 text-neutral-600 dark:text-neutral-400">{visit.notes || 'Visit recorded'}</p>
                  {visit.latitude != null && visit.longitude != null && <p className="mt-1 text-xs text-primary-600">GPS: {visit.latitude.toFixed(5)}, {visit.longitude.toFixed(5)}</p>}
                </div>
              ))}
            </div>
          </section>
        </div>

        <aside className="space-y-5">
          <section className="rounded-lg border border-neutral-200 bg-white p-5 text-center dark:border-neutral-800 dark:bg-surface-dark">
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Outlet QR</h3>
            <img src={outlet.qr_code_url} alt={`QR code for ${outlet.shop_name}`} className="mx-auto mt-4 h-44 w-44 rounded-lg border border-neutral-200 bg-white p-2" />
            <p className="mt-3 text-xs text-neutral-500">Scans to {outlet.qr_code_value}</p>
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Photos</h3>
            <div className="mt-3 grid gap-2">
              {['shop_front', 'inside_shop', 'name_board'].map((photoType) => (
                <label key={photoType} className="flex cursor-pointer items-center justify-between rounded-lg border border-neutral-200 px-3 py-2 text-sm">
                  <span className="inline-flex items-center gap-2"><Camera className="h-4 w-4" />{labelize(photoType)}</span>
                  <input type="file" accept="image/png,image/jpeg,image/webp" className="hidden" onChange={(event) => void uploadPhoto(event.target.files?.[0], photoType)} />
                </label>
              ))}
            </div>
            <div className="mt-4 grid grid-cols-2 gap-2">
              {outlet.photos.map((photo) => (
                <a key={photo.id} href={`${API_ORIGIN}${photo.file_url}`} target="_blank" rel="noreferrer" className="overflow-hidden rounded-lg border border-neutral-200">
                  <img src={`${API_ORIGIN}${photo.file_url}`} alt={labelize(photo.photo_type)} className="h-28 w-full object-cover" />
                </a>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
            <h3 className="font-semibold text-neutral-900 dark:text-neutral-50">Map</h3>
            <div className="mt-4 flex min-h-36 items-center justify-center rounded-lg bg-neutral-50 text-center text-sm text-neutral-500 dark:bg-neutral-800/50">
              <div>
                <MapPinned className="mx-auto mb-2 h-6 w-6 text-primary-600" />
                {outlet.latitude != null && outlet.longitude != null ? `${outlet.latitude}, ${outlet.longitude}` : 'GPS not captured'}
              </div>
            </div>
          </section>
        </aside>
      </div>
    </div>
  )
}

function Info({ label, value, wide = false }: { label: string; value: string; wide?: boolean }) {
  return (
    <div className={wide ? 'sm:col-span-2' : undefined}>
      <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">{label}</p>
      <p className="mt-1 text-sm text-neutral-900 dark:text-neutral-50">{value}</p>
    </div>
  )
}

function labelize(value: string): string {
  return value.split('_').map((part) => part.charAt(0).toUpperCase() + part.slice(1)).join(' ')
}
