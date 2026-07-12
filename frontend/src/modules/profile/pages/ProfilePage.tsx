import { Camera, KeyRound, Save, ShieldCheck, UserCircle } from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { useAuth } from '@/app/providers/AuthProvider'
import { getAssetUrl } from '@/services/api-client'
import { profileService } from '@/services/profile.service'
import type { Profile } from '@/types'

function initials(name: string): string {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

export function ProfilePage() {
  const { refreshUser } = useAuth()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [profile, setProfile] = useState<Profile | null>(null)
  const [fullName, setFullName] = useState('')
  const [phone, setPhone] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false)
  const [profileSaved, setProfileSaved] = useState(false)
  const [error, setError] = useState('')

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isChangingPassword, setIsChangingPassword] = useState(false)
  const [passwordError, setPasswordError] = useState('')
  const [passwordSuccess, setPasswordSuccess] = useState('')

  const load = async () => {
    setIsLoading(true)
    setError('')
    try {
      const response = await profileService.get()
      if (response.data) {
        setProfile(response.data)
        setFullName(response.data.full_name)
        setPhone(response.data.phone ?? '')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load profile')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  const submitProfile = async (event: FormEvent) => {
    event.preventDefault()
    setIsSavingProfile(true)
    setError('')
    setProfileSaved(false)
    try {
      const response = await profileService.update({ full_name: fullName, phone })
      if (response.data) {
        setProfile(response.data)
        await refreshUser()
        setProfileSaved(true)
        setTimeout(() => setProfileSaved(false), 2500)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save profile')
    } finally {
      setIsSavingProfile(false)
    }
  }

  const handleAvatarChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    setIsUploadingAvatar(true)
    setError('')
    try {
      const response = await profileService.uploadAvatar(file)
      if (response.data) {
        setProfile(response.data)
        await refreshUser()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload avatar')
    } finally {
      setIsUploadingAvatar(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const submitPasswordChange = async (event: FormEvent) => {
    event.preventDefault()
    setPasswordError('')
    setPasswordSuccess('')
    if (newPassword.length < 8) {
      setPasswordError('New password must be at least 8 characters.')
      return
    }
    if (newPassword !== confirmPassword) {
      setPasswordError('New password and confirmation do not match.')
      return
    }
    setIsChangingPassword(true)
    try {
      await profileService.changePassword({ current_password: currentPassword, new_password: newPassword })
      setPasswordSuccess('Password changed. Please log in again with your new password.')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      setPasswordError(err instanceof Error ? err.message : 'Failed to change password')
    } finally {
      setIsChangingPassword(false)
    }
  }

  if (isLoading) {
    return <div className="rounded-lg border border-neutral-200 bg-white p-6 text-sm text-neutral-600 dark:border-neutral-800 dark:bg-surface-dark dark:text-neutral-400">Loading profile...</div>
  }

  if (!profile) {
    return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-sm text-red-700">{error || 'Unable to load profile'}</div>
  }

  const avatarUrl = getAssetUrl(profile.profile_image_url)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Profile</h2>
        <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">Manage your personal details and account security.</p>
      </div>

      {error && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</div>}

      <div className="rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <div className="flex flex-col items-center gap-4 sm:flex-row">
          <div className="relative">
            {avatarUrl ? (
              <img src={avatarUrl} alt={profile.full_name} className="h-20 w-20 rounded-full object-cover" />
            ) : (
              <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary-100 text-xl font-semibold text-primary-700 dark:bg-primary-900/40">
                {initials(profile.full_name) || <UserCircle className="h-10 w-10" />}
              </div>
            )}
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploadingAvatar}
              className="absolute -bottom-1 -right-1 rounded-full bg-primary-600 p-1.5 text-white shadow hover:bg-primary-700 disabled:opacity-60"
              aria-label="Change avatar"
            >
              <Camera className="h-3.5 w-3.5" />
            </button>
            <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp" className="hidden" onChange={(e) => void handleAvatarChange(e)} />
          </div>
          <div className="text-center sm:text-left">
            <p className="text-lg font-semibold text-neutral-900 dark:text-neutral-50">{profile.full_name}</p>
            <p className="text-sm text-neutral-500">{profile.email}</p>
            <div className="mt-1 flex flex-wrap justify-center gap-1 sm:justify-start">
              {profile.roles.map((role) => (
                <span key={role} className="rounded-full bg-neutral-100 px-2 py-0.5 text-xs font-medium capitalize text-neutral-700 dark:bg-neutral-800 dark:text-neutral-300">
                  {role.replace('_', ' ')}
                </span>
              ))}
            </div>
          </div>
        </div>

        <dl className="mt-5 grid gap-4 border-t border-neutral-100 pt-5 text-sm sm:grid-cols-2 dark:border-neutral-800">
          {profile.employee_id && (
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Employee ID</dt>
              <dd className="mt-0.5 text-neutral-900 dark:text-neutral-50">{profile.employee_id}</dd>
            </div>
          )}
          {profile.distributor_code && (
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Distributor Code</dt>
              <dd className="mt-0.5 text-neutral-900 dark:text-neutral-50">{profile.distributor_code}</dd>
            </div>
          )}
          {profile.territory && (
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Territory</dt>
              <dd className="mt-0.5 text-neutral-900 dark:text-neutral-50">{profile.territory}</dd>
            </div>
          )}
          {profile.joining_date && (
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Joined</dt>
              <dd className="mt-0.5 text-neutral-900 dark:text-neutral-50">{new Date(profile.joining_date).toLocaleDateString()}</dd>
            </div>
          )}
        </dl>
      </div>

      <form onSubmit={submitProfile} className="space-y-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900 dark:text-neutral-50">
          <UserCircle className="h-4 w-4" />
          Personal Details
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Full Name</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Phone</label>
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Email</label>
            <input value={profile.email} disabled className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-neutral-50 px-3 text-sm text-neutral-500 dark:border-neutral-700 dark:bg-neutral-800" />
          </div>
        </div>
        <div className="flex items-center justify-end gap-3">
          {profileSaved && <span className="text-sm font-medium text-emerald-600">Saved</span>}
          <button
            type="submit"
            disabled={isSavingProfile}
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-primary-600 px-4 text-sm font-semibold text-white hover:bg-primary-700 disabled:opacity-60"
          >
            <Save className="h-4 w-4" />
            {isSavingProfile ? 'Saving...' : 'Save changes'}
          </button>
        </div>
      </form>

      <form onSubmit={submitPasswordChange} className="space-y-4 rounded-lg border border-neutral-200 bg-white p-5 dark:border-neutral-800 dark:bg-surface-dark">
        <div className="flex items-center gap-2 text-sm font-semibold text-neutral-900 dark:text-neutral-50">
          <KeyRound className="h-4 w-4" />
          Change Password
        </div>
        {passwordError && <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">{passwordError}</div>}
        {passwordSuccess && (
          <div className="flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">
            <ShieldCheck className="h-4 w-4" />
            {passwordSuccess}
          </div>
        )}
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Current Password</label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wide text-neutral-500">Confirm New Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="mt-1 h-10 w-full rounded-lg border border-neutral-200 bg-white px-3 text-sm dark:border-neutral-700 dark:bg-neutral-900"
            />
          </div>
        </div>
        <p className="text-xs text-neutral-500">Changing your password will sign you out of all devices.</p>
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isChangingPassword}
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-neutral-200 px-4 text-sm font-semibold text-neutral-700 hover:bg-neutral-50 disabled:opacity-60 dark:border-neutral-700 dark:text-neutral-300"
          >
            <KeyRound className="h-4 w-4" />
            {isChangingPassword ? 'Updating...' : 'Change password'}
          </button>
        </div>
      </form>
    </div>
  )
}
