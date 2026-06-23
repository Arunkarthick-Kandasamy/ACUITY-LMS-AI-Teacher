import { getAccessToken, clearTokens } from '@/services/api'
import * as authService from '@/services/auth'
import type { User, UserRole } from '@/services/types'

export type { UserRole } from '@/services/types'
export type { User }

let currentUser: User | null = null
let listeners: Array<() => void> = []

function notify() {
  listeners.forEach(l => l())
}

const authStore = {
  get user() { return currentUser },

  get isAuthenticated() {
    return !!currentUser && !!getAccessToken()
  },

  async login(email: string, password: string) {
    const data = await authService.login(email, password)
    currentUser = data.user
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
    } catch {
      clearTokens()
    }
    currentUser = null
    notify()
  },

  setUser(user: User) {
    currentUser = user
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
