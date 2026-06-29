import { type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
import { Loader2 } from 'lucide-react'

interface LoadingStateProps extends HTMLAttributes<HTMLDivElement> {
  text?: string
  size?: 'sm' | 'default' | 'lg'
}

const sizeMap = {
  sm: 'h-4 w-4',
  default: 'h-5 w-5',
  lg: 'h-8 w-8',
}

function LoadingState({
  className,
  text,
  size = 'default',
  ...props
}: LoadingStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center gap-3 py-12 text-muted-foreground',
        className
      )}
      {...props}
    >
      <Loader2 className={cn('animate-spin', sizeMap[size])} />
      {text && <p className="text-sm">{text}</p>}
    </div>
  )
}

function LoadingOverlay({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'absolute inset-0 flex items-center justify-center bg-background/60 backdrop-blur-sm z-50',
        className
      )}
      {...props}
    >
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
    </div>
  )
}

export { LoadingState, LoadingOverlay }
export type { LoadingStateProps }
