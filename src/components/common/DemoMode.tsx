import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCyris } from '../../state/CyrisContext'

export function DemoModeButton() {
  const [isRunning, setIsRunning] = useState(false)
  const [stepText, setStepText] = useState('')
  const navigate = useNavigate()
  const { approveControl } = useCyris()

  const startDemo = () => {
    setIsRunning(true)
    setStepText('1. Loading C-Suite Financial Risk Dashboard...')
    navigate('/')

    setTimeout(() => {
      setStepText('2. Identifying top risk drivers & Expected Annual Loss...')
    }, 2500)

    setTimeout(() => {
      setStepText('3. Opening Live IT Model (Digital Twin attack path)...')
      navigate('/twin')
    }, 5500)

    setTimeout(() => {
      setStepText('4. Evaluating Security Protection Counterfactuals...')
      navigate('/counterfactuals')
    }, 9000)

    setTimeout(() => {
      setStepText('5. Applying MFA Protection to harden enterprise twin...')
      approveControl('ctrl-mfa')
    }, 12000)

    setTimeout(() => {
      setStepText('6. Reviewing real-time EAL reduction on Executive Dashboard...')
      navigate('/')
    }, 15000)

    setTimeout(() => {
      setStepText('7. Demo Complete! Risk reduced by ₹85 Lakh.')
      setTimeout(() => {
        setIsRunning(false)
        setStepText('')
      }, 3000)
    }, 18000)
  }

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
      {isRunning && (
        <div
          style={{
            padding: '6px 14px',
            background: 'rgba(59, 130, 246, 0.2)',
            border: '1px solid rgba(59, 130, 246, 0.5)',
            borderRadius: '6px',
            color: '#38bdf8',
            fontSize: '0.82rem',
            fontWeight: 600,
            animation: 'pulse 1.5s infinite'
          }}
        >
          🎬 DEMO MODE: {stepText}
        </div>
      )}

      <button
        type="button"
        className="btn primary"
        onClick={startDemo}
        disabled={isRunning}
        style={{
          padding: '6px 14px',
          fontSize: '0.82rem',
          fontWeight: 600,
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          background: isRunning ? 'rgba(255,255,255,0.1)' : 'linear-gradient(135deg, #2563eb, #0d9488)',
          boxShadow: isRunning ? 'none' : '0 2px 10px rgba(37, 99, 235, 0.4)'
        }}
      >
        <span>{isRunning ? '⏳ Running Demo...' : '▶ Start Guided Demo'}</span>
      </button>
    </div>
  )
}
