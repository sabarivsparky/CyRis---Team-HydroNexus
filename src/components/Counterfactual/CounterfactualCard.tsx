import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCyris } from '../../state/CyrisContext'
import { formatROSI } from '../../utils/formatINR'
import { simulateControlChange } from '../../utils/riskEngine'
import { AnimatedCurrency } from '../common/AnimatedCurrency'
import { TechnicalTooltip, ExpandableTechnicalDetails } from '../common/TechnicalDetails'
import { SimulationLoader } from '../common/SimulationLoader'

export function BeforeAfterMetrics({
  before,
  after,
  reduction,
  cost,
  rosi,
}: {
  before: number
  after: number
  reduction: number
  cost: number
  rosi: number
}) {
  return (
    <div className="cf-pair" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px', margin: '16px 0' }}>
      <div className="metric" style={{ background: 'rgba(239, 68, 68, 0.06)', border: '1px solid rgba(239, 68, 68, 0.2)', padding: '12px', borderRadius: '8px' }}>
        <div className="kicker" style={{ color: '#ef4444', fontSize: '0.72rem' }}>BEFORE YEARLY LOSS</div>
        <div className="num" style={{ fontSize: '1.15rem', marginTop: '4px' }}>
          <AnimatedCurrency value={before} />
        </div>
      </div>

      <div className="metric after" style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '12px', borderRadius: '8px' }}>
        <div className="kicker" style={{ color: '#10b981', fontSize: '0.72rem' }}>AFTER YEARLY LOSS</div>
        <div className="num" style={{ fontSize: '1.25rem', color: '#10b981', fontWeight: 'bold', marginTop: '4px' }}>
          <AnimatedCurrency value={after} />
        </div>
      </div>

      <div className="metric" style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', padding: '12px', borderRadius: '8px' }}>
        <div className="kicker" style={{ color: '#38bdf8', fontSize: '0.72rem' }}>ESTIMATED RISK REDUCTION</div>
        <div className="num" style={{ fontSize: '1.15rem', color: '#38bdf8', fontWeight: 'bold', marginTop: '4px' }}>
          <AnimatedCurrency value={reduction} />
        </div>
      </div>

      <div className="metric" style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '12px', borderRadius: '8px' }}>
        <div className="kicker" style={{ fontSize: '0.72rem' }}>ANNUAL PROTECTION COST</div>
        <div className="num" style={{ fontSize: '1.15rem', marginTop: '4px' }}>
          <AnimatedCurrency value={cost} />
        </div>
      </div>

      <div className="metric" style={{ background: 'rgba(234, 179, 8, 0.08)', border: '1px solid rgba(234, 179, 8, 0.2)', padding: '12px', borderRadius: '8px' }}>
        <div className="kicker" style={{ color: '#eab308', fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
          <span>RETURN FROM INVESTMENT</span>
          <TechnicalTooltip termKey="ROSI" />
        </div>
        <div className="num" style={{ fontSize: '1.15rem', color: '#fde047', fontWeight: 'bold', marginTop: '4px' }}>
          {formatROSI(rosi)}
        </div>
      </div>
    </div>
  )
}

export function CounterfactualCard({ controlId }: { controlId: string }) {
  const { controls, approvedControlIds, baselineEal, approveControl } = useCyris()
  const [isSimulating, setIsSimulating] = useState(false)
  const navigate = useNavigate()

  const control = controls.find((c) => c.id === controlId)
  if (!control) return null

  const approved = approvedControlIds.includes(controlId)
  const prior = approvedControlIds.filter((id) => id !== controlId)
  const sim = simulateControlChange(prior, controlId, controls, baselineEal)

  const handleApprove = () => {
    setIsSimulating(true)
  }

  const handleSimulationComplete = () => {
    setIsSimulating(false)
    approveControl(controlId)
  }

  return (
    <article
      className="card cf-card"
      style={{
        borderColor: approved ? 'rgba(16, 185, 129, 0.5)' : 'var(--border)',
        boxShadow: approved ? '0 4px 20px rgba(16, 185, 129, 0.15)' : undefined,
        transition: 'all 0.3s ease'
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>PROTECTION SCENARIO ANALYSIS</span>
          <TechnicalTooltip termKey="counterfactual" />
        </div>
        {approved && (
          <span style={{ background: '#10b981', color: '#09131d', padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold', textTransform: 'uppercase' }}>
            ✓ ACTIVE ON LIVE IT MODEL
          </span>
        )}
      </div>

      <h2 style={{ marginTop: '4px', fontSize: '1.3rem', color: '#ffffff' }}>{control.name}</h2>
      <p style={{ color: '#cbd5e1', lineHeight: 1.5, fontSize: '0.9rem' }}>{control.description}</p>

      {isSimulating ? (
        <SimulationLoader onComplete={handleSimulationComplete} label={`Simulating Impact for ${control.name}`} />
      ) : (
        <>
          <BeforeAfterMetrics {...sim} />

          <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
              <button
                type="button"
                className={`btn ${approved ? 'secondary' : 'primary'}`}
                disabled={approved}
                onClick={handleApprove}
                style={{
                  padding: '10px 24px',
                  fontSize: '0.95rem',
                  background: approved ? 'rgba(16, 185, 129, 0.2)' : undefined,
                  borderColor: approved ? '#10b981' : undefined,
                  color: approved ? '#10b981' : undefined,
                  fontWeight: 600
                }}
              >
                {approved ? '✓ Protection Applied — IT Model Hardened' : 'Approve & Harden Live IT Model'}
              </button>

              {approved ? (
                <button type="button" className="btn" onClick={() => navigate('/')} style={{ borderColor: '#38bdf8', color: '#38bdf8' }}>
                  See Updated Exposure on Dashboard →
                </button>
              ) : (
                <span className="muted" style={{ fontSize: '0.85rem' }}>
                  🔒 Boardroom decision gate. Hardens the Live IT Model without modifying production code.
                </span>
              )}
            </div>

            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
              {control.frameworkHints.map((hint) => (
                <span key={hint} className="badge" style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#94a3b8', border: '1px solid rgba(255, 255, 255, 0.1)', fontSize: '0.75rem', padding: '2px 8px', borderRadius: '4px' }}>
                  {hint}
                </span>
              ))}
            </div>
          </div>
        </>
      )}

      <ExpandableTechnicalDetails termKey="counterfactual" />
    </article>
  )
}
