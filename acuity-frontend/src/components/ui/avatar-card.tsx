import { type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'
import { Avatar, AvatarImage, AvatarFallback } from './avatar'
import { Badge } from './badge'

interface AvatarCardProps extends HTMLAttributes<HTMLDivElement> {
  name: string
  role?: string
  email?: string
  avatarUrl?: string
  initials?: string
  badge?: string
  badgeVariant?: 'default' | 'secondary' | 'success' | 'warning' | 'brand'
  status?: 'online' | 'offline' | 'away'
}

const statusDot = {
  online: 'bg-success',
  away: 'bg-warning',
  offline: 'bg-muted-foreground/30',
}

function AvatarCard({
  className,
  name,
  role,
  email,
  avatarUrl,
  initials,
  badge: badgeText,
  badgeVariant = 'secondary',
  status,
  ...props
}: AvatarCardProps) {
  return (
    <div
      className={cn(
        'flex items-center gap-3.5 rounded-lg border bg-card p-4',
        'transition-all duration-200 hover:shadow-sm hover:border-primary/20',
        className
      )}
      {...props}
    >
      <div className="relative shrink-0">
        <Avatar className="h-10 w-10">
          <AvatarImage src={avatarUrl} alt={name} />
          <AvatarFallback>{initials ?? name.charAt(0).toUpperCase()}</AvatarFallback>
        </Avatar>
        {status && (
          <span
            className={cn(
              'absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-card',
              statusDot[status]
            )}
          />
        )}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="text-sm font-medium text-foreground truncate">{name}</p>
          {badgeText && <Badge variant={badgeVariant} className="text-[10px] px-1.5 py-0">{badgeText}</Badge>}
        </div>
        {role && <p className="text-xs text-muted-foreground">{role}</p>}
        {email && <p className="text-xs text-muted-foreground/60 truncate mt-0.5">{email}</p>}
      </div>
    </div>
  )
}

export { AvatarCard }
export type { AvatarCardProps }
