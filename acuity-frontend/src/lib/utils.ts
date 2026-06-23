import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatScore(score: number): string {
  return `${Math.round(score)}`
}

export function getScoreColor(score: number): string {
  if (score >= 75) return 'text-emerald-600'
  if (score >= 50) return 'text-amber-600'
  return 'text-red-600'
}

export function getScoreBgColor(score: number): string {
  if (score >= 75) return 'bg-emerald-500'
  if (score >= 50) return 'bg-amber-500'
  return 'bg-red-500'
}

export function getTrackLabel(score: number): { label: string; color: string; desc: string } {
  if (score >= 75) return {
    label: 'Good Learner Track',
    color: 'text-emerald-600 bg-emerald-50',
    desc: 'Advanced concept-based learning with HOT questions'
  }
  return {
    label: 'Support Learner Track',
    color: 'text-amber-600 bg-amber-50',
    desc: 'Simplified step-by-step with example-driven teaching'
  }
}

export function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat('en-US', { month: 'short', day: 'numeric', year: 'numeric' }).format(date)
}

export function timeAgo(dateStr: string): string {
  return dateStr
}

export function getParamScore(name: string, value: number): { label: string; icon: string } {
  const config: Record<string, { label: string; icon: string }> = {
    correctness: { label: 'Correctness', icon: '✓' },
    responseTime: { label: 'Response Time', icon: '⏱' },
    retries: { label: 'Retries', icon: '↻' },
    skips: { label: 'Skips', icon: '→' },
  }
  return config[name] || { label: name, icon: '•' }
}
