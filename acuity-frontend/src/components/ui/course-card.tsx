import { type HTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { Badge } from './badge'
import { Progress } from './progress'

interface CourseCardProps extends HTMLAttributes<HTMLDivElement> {
  title: string
  description?: string
  image?: string
  badge?: string
  badgeVariant?: 'default' | 'secondary' | 'success' | 'warning' | 'brand'
  progress?: number
  icon?: ReactNode
  footer?: ReactNode
}

function CourseCard({
  className,
  title,
  description,
  image,
  badge: badgeText,
  badgeVariant = 'brand',
  progress,
  icon,
  footer,
  ...props
}: CourseCardProps) {
  return (
    <div
      className={cn(
        'group relative overflow-hidden rounded-xl border bg-card text-card-foreground shadow-sm',
        'transition-all duration-200 hover:shadow-md hover:-translate-y-0.5',
        'cursor-pointer',
        className
      )}
      {...props}
    >
      {image && (
        <div className="aspect-video w-full overflow-hidden bg-muted">
          <img
            src={image}
            alt={title}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        </div>
      )}
      <div className="p-5 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 min-w-0 flex-1">
            <div className="flex items-center gap-2">
              {icon && <span className="shrink-0">{icon}</span>}
              <h3 className="font-semibold text-foreground leading-tight line-clamp-1">
                {title}
              </h3>
            </div>
            {description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {description}
              </p>
            )}
          </div>
          {badgeText && (
            <Badge variant={badgeVariant} className="shrink-0">
              {badgeText}
            </Badge>
          )}
        </div>
        {progress !== undefined && (
          <div className="space-y-1.5">
            <Progress value={progress} />
            <p className="text-xs text-muted-foreground">{Math.round(progress)}% complete</p>
          </div>
        )}
        {footer && <div className="pt-2 border-t border-border">{footer}</div>}
      </div>
    </div>
  )
}

export { CourseCard }
export type { CourseCardProps }
