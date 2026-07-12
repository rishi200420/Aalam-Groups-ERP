import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { brand } from '@/constants/colors'

export function SplashPage() {
  const navigate = useNavigate()
  const { isAuthenticated, isLoading, isFounder, isDistributor } = useAuth()
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 4, 100))
    }, 60)

    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (isLoading || progress < 100) return

    const timer = setTimeout(() => {
      if (isAuthenticated) {
        if (isFounder) {
          navigate('/dashboard/founder', { replace: true })
        } else if (isDistributor) {
          navigate('/dashboard/distributor', { replace: true })
        } else {
          navigate('/dashboard/founder', { replace: true })
        }
      } else {
        navigate('/login', { replace: true })
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [isLoading, progress, isAuthenticated, isFounder, isDistributor, navigate])

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-background-dark px-6">
      <div className="flex flex-col items-center text-center max-w-sm">
        <div className="w-20 h-20 rounded-2xl bg-primary-600 flex items-center justify-center shadow-lg mb-6">
          <span className="text-white text-3xl font-bold">A</span>
        </div>
        <h1 className="text-2xl font-bold text-neutral-900 dark:text-neutral-50">{brand.name}</h1>
        <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">{brand.tagline}</p>
        <div className="w-48 h-1 bg-neutral-200 dark:bg-neutral-700 rounded-full mt-10 overflow-hidden">
          <div
            className="h-full bg-primary-600 transition-all duration-100 ease-out"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="mt-3 text-xs text-neutral-500">Loading platform...</p>
      </div>
    </div>
  )
}
