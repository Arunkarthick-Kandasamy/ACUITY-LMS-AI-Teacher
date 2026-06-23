export type UserRole = 'student' | 'parent' | 'admin' | null

interface User {
  id: string
  name: string
  email: string
  role: Exclude<UserRole, null>
  avatar?: string
}

// Simple in-memory auth store (replace with real auth later)
let currentUser: User | null = null
let listeners: Array<() => void> = []

const authStore = {
  get user() { return currentUser },

  login(role: Exclude<UserRole, null>) {
    currentUser = {
      id: '1',
      name: role === 'student' ? 'Abinaya' : role === 'parent' ? 'Rajesh Kumar' : 'Admin',
      email: role === 'student' ? 'abinaya@example.com' : role === 'parent' ? 'rajesh@example.com' : 'admin@acuity.com',
      role,
    }
    this.notify()
  },

  logout() {
    currentUser = null
    this.notify()
  },

  subscribe(listener: () => void) {
    listeners.push(listener)
    return () => {
      listeners = listeners.filter(l => l !== listener)
    }
  },

  notify() {
    listeners.forEach(l => l())
  }
}

export { authStore }
export type { User }
