interface PlaceholderContentProps {
  title: string
  description?: string
}

export function PlaceholderContent({
  title,
  description = 'This module will be implemented in the next development phase.',
}: PlaceholderContentProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[320px] rounded-xl border border-dashed border-neutral-200 dark:border-neutral-700 bg-white dark:bg-surface-dark p-8 text-center">
      <div className="w-12 h-12 rounded-full bg-primary-50 dark:bg-primary-600/20 flex items-center justify-center mb-4">
        <span className="text-primary-600 font-semibold text-lg">A</span>
      </div>
      <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-50 mb-2">{title}</h2>
      <p className="text-sm text-neutral-600 dark:text-neutral-400 max-w-md">{description}</p>
    </div>
  )
}
