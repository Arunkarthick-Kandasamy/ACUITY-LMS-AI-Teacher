import * as authService from '@/services/auth'
import type { User, UserRole } from '@/services/types'

export type { UserRole } from '@/services/types'
export type { User }

const STORAGE_KEY = 'acuity_current_user'

let currentUser: User | null = (() => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : null
  } catch {
    return null
  }
})()
let listeners: Array<() => void> = []

function notify() {
  listeners.forEach(l => l())
}

const authStore = {
  get user() { return currentUser },

  get isAuthenticated() {
    return !!currentUser
  },

  async login(email: string, password: string, role: UserRole) {
    const data = await authService.login(email, password, role)
    currentUser = data.user
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data.user))
    notify()
    return data
  },

  async register(email: string, password: string, fullName: string, role: UserRole) {
    const user = await authService.register(email, password, fullName, role)
    return user
  },

  async logout() {
    try {
      await authService.logout()
    } catch {}
    currentUser = null
    localStorage.removeItem(STORAGE_KEY)
    notify()
  },

  setUser(user: User) {
    currentUser = user
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
    notify()
  },

  subscribe(listener: () => void) {
    listeners.push(listener)
    return () => {
      listeners = listeners.filter(l => l !== listener)
    }
  },
}

export { authStore }
