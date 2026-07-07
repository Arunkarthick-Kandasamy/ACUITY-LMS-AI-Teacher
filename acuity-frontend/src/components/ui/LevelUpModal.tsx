import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Star, Zap } from 'lucide-react'

interface LevelUpModalProps {
  level: number
  show: boolean
  onClose: () => void
}

export function LevelUpModal({ level, show, onClose }: LevelUpModalProps) {
  const [stars, setStars] = useState<{ id: number; x: number; delay: number }[]>([])

  useEffect(() => {
    if (show) {
      setStars(
        Array.from({ length: 8 }, (_, i) => ({
          id: i,
          x: Math.random() * 80 + 10,
          delay: i * 0.1,
        }))
      )
      const timer = setTimeout(onClose, 3000)
      return () => clearTimeout(timer)
    }
  }, [show, onClose])

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm"
        >
          <motion.div
            initial={{ scale: 0.5, rotate: -10 }}
            animate={{ scale: 1, rotate: 0 }}
            exit={{ scale: 0.5, rotate: 10 }}
            transition={{ type: 'spring', damping: 12, stiffness: 200 }}
            className="bg-gradient-to-br from-yellow-400 via-amber-500 to-orange-500 rounded-3xl p-8 text-center shadow-2xl max-w-xs mx-4"
          >
            <div className="relative mb-4">
              <div className="w-20 h-20 rounded-full bg-white/20 mx-auto flex items-center justify-center">
                <Zap className="w-10 h-10 text-white" />
              </div>
              {stars.map(s => (
                <motion.div
                  key={s.id}
                  initial={{ opacity: 0, scale: 0, y: 0 }}
                  animate={{ opacity: [0, 1, 0], scale: [0, 1.5, 0], y: -60 }}
                  transition={{ duration: 1.5, delay: s.delay, repeat: Infinity, repeatDelay: 2 }}
                  className="absolute top-0"
                  style={{ left: `${s.x}%` }}
                >
                  <Star className="w-5 h-5 text-yellow-200 fill-yellow-200" />
                </motion.div>
              ))}
            </div>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, type: 'spring', damping: 10 }}
            >
              <Sparkles className="w-8 h-8 text-yellow-200 mx-auto mb-2" />
              <h2 className="text-3xl font-bold text-white mb-1">LEVEL UP!</h2>
              <div className="text-6xl font-black text-white mb-2">{level}</div>
              <p className="text-yellow-100 font-medium">You're on fire! Keep learning!</p>
            </motion.div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
