import { useEffect, useRef, useState } from 'react'
import { animate, useInView } from 'framer-motion'

interface UseAnimatedCounterOptions {
  from?: number
  to: number
  duration?: number
  delay?: number
}

export function useAnimatedCounter({ from = 0, to, duration = 2, delay = 0 }: UseAnimatedCounterOptions) {
  const [count, setCount] = useState(from)
  const ref = useRef<HTMLDivElement>(null)
  const isInView = useInView(ref, { once: true, margin: "-50px" })

  useEffect(() => {
    if (!isInView) return

    const timer = setTimeout(() => {
      const controls = animate(from, to, {
        duration,
        ease: [0.16, 1, 0.3, 1],
        onUpdate(value) {
          setCount(Math.round(value))
        },
      })
      return controls.stop
    }, delay * 1000)

    return () => clearTimeout(timer)
  }, [isInView, from, to, duration, delay])

  return { count, ref }
}
