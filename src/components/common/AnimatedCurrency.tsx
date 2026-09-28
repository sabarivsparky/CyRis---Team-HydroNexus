import { useEffect, useState, useRef } from 'react'
import { formatINR } from '../../utils/formatINR'

interface AnimatedCurrencyProps {
  value: number
  duration?: number
  className?: string
  style?: React.CSSProperties
}

export function AnimatedCurrency({ value, duration = 1000, className, style }: AnimatedCurrencyProps) {
  const [displayValue, setDisplayValue] = useState(value)
  const prevValueRef = useRef(value)
  const animFrameRef = useRef<number | null>(null)

  useEffect(() => {
    // Respect reduced motion preference
    const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if (prefersReduced) {
      setDisplayValue(value)
      prevValueRef.current = value
      return
    }

    const startVal = prevValueRef.current
    const endVal = value
    if (startVal === endVal) return

    const startTime = performance.now()

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / duration, 1)

      // Ease-out cubic formula
      const easeOut = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(startVal + (endVal - startVal) * easeOut)

      setDisplayValue(current)

      if (progress < 1) {
        animFrameRef.current = requestAnimationFrame(animate)
      } else {
        setDisplayValue(endVal)
        prevValueRef.current = endVal
      }
    }

    animFrameRef.current = requestAnimationFrame(animate)

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    }
  }, [value, duration])

  return (
    <span className={className} style={{ transition: 'color 0.3s ease', ...style }}>
      {formatINR(displayValue)}
    </span>
  )
}
