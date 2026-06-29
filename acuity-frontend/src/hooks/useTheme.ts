import { useCallback, useLayoutEffect, useSyncExternalStore } from 'react'

type Theme = 'light' | 'dark'

function getSystemTheme(): Theme {
  if (typeof window === 'undefined') return 'light'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function getStoredTheme(): Theme | null {
  try {
    const stored = localStorage.getItem('theme')
    if (stored === 'light' || stored === 'dark') return stored
  } catch {}
  return null
}

function getTheme(): Theme {
  return getStoredTheme() ?? getSystemTheme()
}

function setDOMTheme(theme: Theme) {
  const root = document.documentElement
  root.classList.toggle('dark', theme === 'dark')
}

function subscribeToSystemTheme(callback: () => void): () => void {
  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  mq.addEventListener('change', callback)
  return () => mq.removeEventListener('change', callback)
}

const listeners = new Set<() => void>()

function notifyListeners() {
  listeners.forEach(fn => fn())
}

function subscribe(callback: () => void): () => void {
  listeners.add(callback)
  return () => { listeners.delete(callback) }
}

function getSnapshot(): Theme {
  return getTheme()
}

let serverSnapshot: Theme = 'light'

function getServerSnapshot(): Theme {
  return serverSnapshot
}

export function setTheme(theme: Theme) {
  try {
    localStorage.setItem('theme', theme)
  } catch {}
  setDOMTheme(theme)
  notifyListeners()
}

export function toggleTheme() {
  const next = getTheme() === 'dark' ? 'light' : 'dark'
  setTheme(next)
}

export function useTheme() {
  const theme = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)

  useLayoutEffect(() => {
    setDOMTheme(theme)
  }, [theme])

  useLayoutEffect(() => {
    const unsub = subscribeToSystemTheme(() => {
      if (!getStoredTheme()) {
        notifyListeners()
      }
    })
    return unsub
  }, [])

  const toggle = useCallback(() => {
    toggleTheme()
  }, [])

  const set = useCallback((t: Theme) => {
    setTheme(t)
  }, [])

  return { theme, toggle, set, isDark: theme === 'dark' }
}
