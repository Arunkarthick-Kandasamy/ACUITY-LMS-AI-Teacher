import { useCallback, useRef } from 'react'

let audioCtx: AudioContext | null = null

function getAudioCtx(): AudioContext {
  if (!audioCtx) {
    audioCtx = new AudioContext()
  }
  return audioCtx
}

function playTone(frequency: number, duration: number, type: OscillatorType = 'sine', volume = 0.15) {
  try {
    const ctx = getAudioCtx()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.type = type
    osc.frequency.setValueAtTime(frequency, ctx.currentTime)
    gain.gain.setValueAtTime(volume, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration)
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + duration)
  } catch {}
}

export function useSound() {
  const enabledRef = useRef(true)

  const playCorrect = useCallback(() => {
    if (!enabledRef.current) return
    playTone(523.25, 0.15, 'sine', 0.12)
    setTimeout(() => playTone(659.25, 0.15, 'sine', 0.12), 100)
    setTimeout(() => playTone(783.99, 0.2, 'sine', 0.12), 200)
  }, [])

  const playIncorrect = useCallback(() => {
    if (!enabledRef.current) return
    playTone(200, 0.3, 'square', 0.08)
    setTimeout(() => playTone(180, 0.4, 'square', 0.08), 200)
  }, [])

  const playLevelUp = useCallback(() => {
    if (!enabledRef.current) return
    const notes = [523.25, 659.25, 783.99, 1046.5]
    notes.forEach((freq, i) => {
      setTimeout(() => playTone(freq, 0.3, 'sine', 0.12), i * 150)
    })
  }, [])

  const playBadge = useCallback(() => {
    if (!enabledRef.current) return
    playTone(783.99, 0.12, 'sine', 0.1)
    setTimeout(() => playTone(1046.5, 0.15, 'sine', 0.1), 80)
    setTimeout(() => playTone(1318.5, 0.2, 'sine', 0.1), 160)
  }, [])

  const playClick = useCallback(() => {
    if (!enabledRef.current) return
    playTone(800, 0.05, 'sine', 0.06)
  }, [])

  const toggleSound = useCallback(() => {
    enabledRef.current = !enabledRef.current
    return enabledRef.current
  }, [])

  return { playCorrect, playIncorrect, playLevelUp, playBadge, playClick, toggleSound }
}
