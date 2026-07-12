import { createContext, useContext, useState, type ReactNode } from 'react'
import type { BrandFilter } from '@/types'

interface BrandFilterContextValue {
  brand: BrandFilter
  setBrand: (brand: BrandFilter) => void
}

const BrandFilterContext = createContext<BrandFilterContextValue | undefined>(undefined)

export function BrandFilterProvider({ children }: { children: ReactNode }) {
  const [brand, setBrand] = useState<BrandFilter>('all')

  return (
    <BrandFilterContext.Provider value={{ brand, setBrand }}>
      {children}
    </BrandFilterContext.Provider>
  )
}

export function useBrandFilter() {
  const context = useContext(BrandFilterContext)
  if (!context) {
    throw new Error('useBrandFilter must be used within BrandFilterProvider')
  }
  return context
}
