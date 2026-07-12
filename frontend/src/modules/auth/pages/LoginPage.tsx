import { Eye, EyeOff, Lock, Mail } from 'lucide-react'
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { brand } from '@/constants/colors'
import { cn } from '@/utils/cn'

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const from = (location.state as { from?: string } | null)?.from

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const user = await login(email.trim(), password, rememberMe)
      const role = user.primary_role ?? user.roles[0]

      if (from && from !== '/login') {
        navigate(from, { replace: true })
        return
      }

      if (role === 'founder' || role === 'super_admin') {
        navigate('/dashboard/founder', { replace: true })
      } else if (role === 'distributor') {
        navigate('/dashboard/distributor', { replace: true })
      } else {
        navigate('/dashboard/founder', { replace: true })
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to sign in. Please try again.'
      setError(message.includes('401') ? 'Invalid email or password' : message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-background dark:bg-background-dark">
      <div className="hidden lg:flex flex-col justify-between p-12 bg-gradient-to-br from-primary-600 to-primary-700 text-white">
        <div>
          <div className="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center mb-8">
            <span className="text-2xl font-bold">A</span>
          </div>
          <h1 className="text-4xl font-bold leading-tight">{brand.appName}</h1>
          <p className="mt-4 text-white/80 text-lg max-w-md">
            Powering TASTIQ & LEMURIA operations across Chennai territories.
          </p>
          <div className="w-16 h-1 bg-gold-500 rounded mt-8" />
        </div>
        <p className="text-sm text-white/60">© {new Date().getFullYear()} {brand.name}</p>
      </div>

      <div className="flex items-center justify-center p-6 sm:p-10">
        <div className="w-full max-w-md">
          <div className="lg:hidden mb-8 text-center">
            <div className="inline-flex w-12 h-12 rounded-xl bg-primary-600 items-center justify-center mb-3">
              <span className="text-white font-bold text-lg">A</span>
            </div>
            <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-50">{brand.appName}</h2>
          </div>

          <div className="bg-white dark:bg-surface-dark rounded-2xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-6 sm:p-8">
            <h2 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Welcome back</h2>
            <p className="mt-1 text-sm text-neutral-600 dark:text-neutral-400">Sign in to your account</p>

            {error && (
              <div className="mt-4 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/30 dark:text-red-300">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    id="email"
                    type="email"
                    required
                    autoComplete="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@aalamgroups.com"
                    className="w-full h-11 pl-10 pr-3 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary-600/20 focus:border-primary-600"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Enter your password"
                    className="w-full h-11 pl-10 pr-10 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-neutral-900 dark:text-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary-600/20 focus:border-primary-600"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword((prev) => !prev)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-neutral-600"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="rounded border-neutral-300 text-primary-600 focus:ring-primary-600"
                  />
                  Remember me
                </label>
                <Link to="/forgot-password" className="text-sm font-medium text-primary-600 hover:text-primary-700">
                  Forgot password?
                </Link>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className={cn(
                  'w-full h-11 rounded-lg bg-primary-600 text-white font-medium transition-colors',
                  'hover:bg-primary-700 disabled:opacity-60 disabled:cursor-not-allowed',
                )}
              >
                {isSubmitting ? 'Signing in...' : 'Sign In'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
