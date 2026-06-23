import { cn } from '@/lib/utils'
import { ButtonHTMLAttributes, forwardRef } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-navy-800/20 disabled:opacity-50 disabled:pointer-events-none',
          variant === 'primary' && 'bg-navy-800 text-white hover:bg-navy-700 shadow-sm hover:shadow-md',
          variant === 'secondary' && 'border border-slate-300 bg-white text-slate-700 hover:bg-slate-50',
          variant === 'ghost' && 'text-slate-600 hover:bg-slate-100',
          variant === 'danger' && 'bg-red-600 text-white hover:bg-red-700 shadow-sm',
          size === 'sm' && 'px-3 py-1.5 text-xs',
          size === 'md' && 'px-5 py-2.5 text-sm',
          size === 'lg' && 'px-6 py-3 text-base',
          className
        )}
        {...props}
      >
        {children}
      </button>
    )
  }
)
Button.displayName = 'Button'

export { Button }
