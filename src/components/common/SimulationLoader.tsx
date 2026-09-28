import { useEffect, useState } from 'react'

interface SimulationLoaderProps {
  onComplete?: () => void
  duration?: number
  label?: string
}

export function SimulationLoader({ onComplete, duration = 1400, label = 'Simulating Cyber Risk Scenarios' }: SimulationLoaderProps) {
  const [scenariosCount, setScenariosCount] = useState(0)
  const [stage, setStage] = useState('Initializing stochastic engine...')

  useEffect(() => {
    const startTime = performance.now()
    const targetScenarios = 10000

    const interval = setInterval(() => {
      const elapsed = performance.now() - startTime
      const progress = Math.min(elapsed / duration, 1)

      const current = Math.round(progress * targetScenarios)
      setScenariosCount(current)

      if (progress < 0.3) {
        setStage('Tracing attack path probabilities...')
      } else if (progress < 0.7) {
        setStage('Executing 10,000 Monte Carlo iterations...')
      } else if (progress < 0.95) {
        setStage('Quantifying financial loss distributions...')
      } else {
        setStage('Simulation complete!')
      }

      if (progress >= 1) {
        clearInterval(interval)
        if (onComplete) onComplete()
      }
    }, 40)

    return () => clearInterval(interval)
  }, [duration, onComplete])

  return (
    <div
      style={{
        padding: '20px',
        background: 'rgba(15, 23, 42, 0.95)',
        border: '1px solid rgba(59, 130, 246, 0.4)',
        borderRadius: '10px',
        textAlign: 'center',
        boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
        maxWidth: '450px',
        margin: '16px auto'
      }}
    >
      <div style={{ fontSize: '0.8rem', color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.08em', fontWeight: 600 }}>
        {label}
      </div>

      <div style={{ fontSize: '1.8rem', fontWeight: 'bold', color: '#ffffff', margin: '12px 0 4px 0', fontFamily: 'IBM Plex Mono, monospace' }}>
        {scenariosCount.toLocaleString()} / 10,000
      </div>
      <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginBottom: '16px' }}>Scenarios Analyzed</div>

      {/* Progress Bar */}
      <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', overflow: 'hidden' }}>
        <div
          style={{
            height: '100%',
            width: `${(scenariosCount / 10000) * 100}%`,
            background: 'linear-gradient(90deg, #3b82f6, #10b981)',
            transition: 'width 0.05s linear'
          }}
        />
      </div>

      <div style={{ fontSize: '0.82rem', color: '#cbd5e1', marginTop: '12px', fontStyle: 'italic' }}>
        {stage}
      </div>
    </div>
  )
}
