import { type HTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { CheckCircle2, Circle, Lock } from 'lucide-react'
import { Badge } from './badge'

type LessonStatus = 'completed' | 'in-progress' | 'locked' | 'available'

interface LessonCardProps extends HTMLAttributes<HTMLDivElement> {
  title: string
  description?: string
  status?: LessonStatus
  duration?: string
  icon?: ReactNode
  index?: number
}

const statusConfig: Record<LessonStatus, {
  icon: ReactNode
  badgeLabel: string
  badgeVariant: 'success' | 'warning' | 'secondary' | 'brand'
}> = {
  completed: {
    icon: <CheckCircle2 className="h-5 w-5 text-success" />,
    badgeLabel: 'Completed',
    badgeVariant: 'success',
  },
  'in-progress': {
    icon: <Circle className="h-5 w-5 text-primary fill-primary/20" />,
    badgeLabel: 'In Progress',
    badgeVariant: 'warning',
  },
  locked: {
    icon: <Lock className="h-5 w-5 text-muted-foreground/40" />,
    badgeLabel: 'Locked',
    badgeVariant: 'secondary',
  },
  available: {
    icon: <Circle className="h-5 w-5 text-muted-foreground/30" />,
    badgeLabel: 'Available',
    badgeVariant: 'brand',
  },
}

function LessonCard({
  className,
  title,
  description,
  status = 'available',
  duration,
  icon,
  index,
  ...props
}: LessonCardProps) {
  const config = statusConfig[status]
  const isLocked = status === 'locked'
  const isCompleted = status === 'completed'

  return (
    <div
      className={cn(
        'group relative flex items-start gap-4 rounded-lg border bg-card px-4 py-3.5',
        'transition-all duration-200',
        isLocked
          ? 'opacity-60 cursor-not-allowed'
          : 'hover:shadow-sm hover:border-primary/30 cursor-pointer active:scale-[0.99]',
        isCompleted && 'border-success/20',
        className
      )}
      {...props}
    >
      {index !== undefined && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-semibold text-muted-foreground">
          {index}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <h4 className={cn(
            'text-sm font-medium leading-snug',
            isCompleted ? 'text-muted-foreground line-through decoration-muted-foreground/30' : 'text-foreground'
          )}>
            {title}
          </h4>
          <Badge variant={config.badgeVariant} className="text-[10px] px-1.5 py-0">
            {config.badgeLabel}
          </Badge>
        </div>
        {description && (
          <p className="text-xs text-muted-foreground mt-1 line-clamp-1">
            {description}
          </p>
        )}
        {duration && (
          <p className="text-xs text-muted-foreground/60 mt-1.5">{duration}</p>
        )}
      </div>
      <div className="shrink-0 mt-0.5">
        {icon ?? config.icon}
      </div>
    </div>
  )
}

export { LessonCard }
export type { LessonCardProps, LessonStatus }
