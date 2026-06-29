import { type HTMLAttributes, type ReactNode } from 'react'
import { cn } from '@/lib/utils'
import { Badge } from './badge'
import { Progress } from './progress'
import { Clock, HelpCircle } from 'lucide-react'

interface QuizCardProps extends HTMLAttributes<HTMLDivElement> {
  title: string
  description?: string
  questionCount?: number
  timeLimit?: string
  score?: number
  passingScore?: number
  status?: 'not-started' | 'in-progress' | 'passed' | 'failed'
  icon?: ReactNode
  footer?: ReactNode
}

const statusBadge: Record<string, { label: string; variant: 'success' | 'warning' | 'destructive' | 'secondary' }> = {
  passed: { label: 'Passed', variant: 'success' },
  failed: { label: 'Failed', variant: 'destructive' },
  'in-progress': { label: 'In Progress', variant: 'warning' },
  'not-started': { label: 'Not Started', variant: 'secondary' },
}

function QuizCard({
  className,
  title,
  description,
  questionCount,
  timeLimit,
  score,
  passingScore,
  status = 'not-started',
  icon,
  footer,
  ...props
}: QuizCardProps) {
  const badge = statusBadge[status]

  return (
    <div
      className={cn(
        'group relative rounded-xl border bg-card text-card-foreground shadow-sm',
        'transition-all duration-200 hover:shadow-md hover:-translate-y-0.5',
        'cursor-pointer',
        className
      )}
      {...props}
    >
      <div className="p-5 space-y-3">
        <div className="flex items-start justify-between gap-2">
          <div className="space-y-1 min-w-0 flex-1">
            <div className="flex items-center gap-2">
              {icon ?? <HelpCircle className="h-4 w-4 text-primary" />}
              <h3 className="font-semibold text-foreground leading-tight line-clamp-1">
                {title}
              </h3>
            </div>
            {description && (
              <p className="text-sm text-muted-foreground line-clamp-1">
                {description}
              </p>
            )}
          </div>
          <Badge variant={badge.variant} className="shrink-0">{badge.label}</Badge>
        </div>

        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          {questionCount && (
            <span className="flex items-center gap-1">
              <HelpCircle className="h-3.5 w-3.5" />
              {questionCount} questions
            </span>
          )}
          {timeLimit && (
            <span className="flex items-center gap-1">
              <Clock className="h-3.5 w-3.5" />
              {timeLimit}
            </span>
          )}
        </div>

        {score !== undefined && (
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-muted-foreground">Score</span>
              <span className={cn(
                'font-medium',
                score >= (passingScore ?? 70) ? 'text-success' : 'text-destructive'
              )}>
                {Math.round(score)}%
              </span>
            </div>
            <Progress value={score} className={cn(score >= (passingScore ?? 70) ? 'progress-success' : '')} />
          </div>
        )}

        {footer && <div className="pt-2 border-t border-border">{footer}</div>}
      </div>
    </div>
  )
}

export { QuizCard }
export type { QuizCardProps }
