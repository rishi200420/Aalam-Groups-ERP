import { ArrowLeft, Mail } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { authService } from '@/services/auth.service'
import { cn } from '@/utils/cn'

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      await authService.forgotPassword(email.trim())
      setIsSubmitted(true)
    } catch {
      setError('Unable to process request. Please try again later.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background dark:bg-background-dark p-6">
      <div className="w-full max-w-md">
        <Link
          to="/login"
          className="inline-flex items-center gap-2 text-sm text-neutral-600 dark:text-neutral-400 hover:text-primary-600 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to login
        </Link>

        <div className="bg-white dark:bg-surface-dark rounded-2xl shadow-sm border border-neutral-200 dark:border-neutral-800 p-6 sm:p-8">
          <h1 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-50">Forgot password?</h1>
          <p className="mt-2 text-sm text-neutral-600 dark:text-neutral-400">
            Enter your email and we&apos;ll send reset instructions if an account exists.
          </p>

          {isSubmitted ? (
            <div className="mt-6 rounded-lg border border-primary-200 bg-primary-50 dark:border-primary-900/40 dark:bg-primary-600/10 p-4 text-sm text-primary-700 dark:text-primary-100">
              If an account exists for <strong>{email}</strong>, password reset instructions have been sent.
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="mt-6 space-y-4">
              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <div>
                <label htmlFor="reset-email" className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1.5">
                  Email address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
                  <input
                    id="reset-email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@aalamgroups.com"
                    className="w-full h-11 pl-10 pr-3 rounded-lg border border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className={cn(
                  'w-full h-11 rounded-lg bg-primary-600 text-white font-medium hover:bg-primary-700',
                  'disabled:opacity-60 disabled:cursor-not-allowed',
                )}
              >
                {isSubmitting ? 'Sending...' : 'Send Reset Link'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
