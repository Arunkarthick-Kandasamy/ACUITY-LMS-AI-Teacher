import { type HTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface DashboardWidgetProps extends HTMLAttributes<HTMLDivElement> {
  title?: string
  subtitle?: string
  headerAction?: ReactNode
  variant?: 'default' | 'compact'
}

function DashboardWidget({
  className,
  title,
  subtitle,
  headerAction,
  variant = 'default',
  children,
  ...props
}: DashboardWidgetProps) {
  const hasHeader = title || subtitle || headerAction

  return (
    <div
      className={cn(
        'rounded-xl border bg-card text-card-foreground shadow-sm',
        className
      )}
      {...props}
    >
      {hasHeader && (
        <div className="flex items-center justify-between px-6 pt-6 pb-4">
          <div className="space-y-0.5">
            {title && (
              <h3 className="text-sm font-semibold text-foreground">{title}</h3>
            )}
            {subtitle && (
              <p className="text-xs text-muted-foreground">{subtitle}</p>
            )}
          </div>
          {headerAction && (
            <div className="flex items-center gap-2">{headerAction}</div>
          )}
        </div>
      )}
      <div className={cn(
        variant === 'compact' ? 'px-6 pb-4' : 'px-6 pb-6'
      )}>
        {children}
      </div>
    </div>
  )
}

export { DashboardWidget }
export type { DashboardWidgetProps }
