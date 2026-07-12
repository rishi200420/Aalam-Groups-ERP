import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '@/app/providers/AuthProvider'
import { BrandFilterProvider } from '@/app/providers/BrandFilterProvider'
import { ThemeProvider } from '@/app/providers/ThemeProvider'
import type { ReactNode } from 'react'

interface AppProvidersProps {
  children: ReactNode
}

export function AppProviders({ children }: AppProvidersProps) {
  return (
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <BrandFilterProvider>{children}</BrandFilterProvider>
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}
