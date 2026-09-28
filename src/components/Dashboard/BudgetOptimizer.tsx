import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCyris } from '../../state/CyrisContext'
import { formatROSI, formatINRDelta } from '../../utils/formatINR'
import { optimizeBudget, investmentCurve } from '../../utils/riskEngine'
import { AnimatedCurrency } from '../common/AnimatedCurrency'
import { TechnicalTooltip, ExpandableTechnicalDetails } from '../common/TechnicalDetails'
import { SimulationLoader } from '../common/SimulationLoader'

export function BudgetOptimizer() {
  const { budget, setBudget, controls, baselineEal, approvedControlIds, applyBudgetPlan } = useCyris()
  const [isSimulating, setIsSimulating] = useState(false)

  const plan = useMemo(
    () => optimizeBudget(budget, controls, baselineEal, approvedControlIds),
    [budget, controls, baselineEal, approvedControlIds],
  )
  const max = controls.reduce((s, c) => s + c.cost, 0)

  const handleApprove = () => {
    setIsSimulating(true)
  }

  const handleSimulationComplete = () => {
    setIsSimulating(false)
    applyBudgetPlan()
  }

  return (
    <section className="card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(30, 41, 59, 0.7))', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
      <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span>CAPITAL ALLOCATION & PROTECTION PLANNER</span>
        <TechnicalTooltip termKey="counterfactual" />
      </div>

      <h2 style={{ fontSize: '1.3rem', color: '#ffffff', marginTop: '4px' }}>
        RECOMMENDED PROTECTION PORTFOLIO
      </h2>
      <p style={{ color: '#94a3b8', fontSize: '0.88rem', margin: '2px 0 16px 0' }}>
        Adjust the budget ceiling to automatically select the optimal combination of safeguards for maximum risk reduction.
      </p>

      {isSimulating ? (
        <SimulationLoader onComplete={handleSimulationComplete} label="Simulating Portfolio Risk Reduction" />
      ) : (
        <>
          <div style={{ background: 'rgba(0,0,0,0.25)', padding: '14px 16px', borderRadius: '8px', border: '1px solid var(--border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <label htmlFor="budget" style={{ fontSize: '0.9rem', color: '#e2e8f0', fontWeight: 600 }}>
                MAXIMUM ANNUAL BUDGET CEILING:
              </label>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#38bdf8', fontFamily: 'IBM Plex Mono, monospace' }}>
                <AnimatedCurrency value={budget} />
              </div>
            </div>

            <input
              id="budget"
              type="range"
              min={0}
              max={max}
              step={50_000}
              value={budget}
              onChange={(e) => setBudget(Number(e.target.value))}
              style={{ width: '100%', cursor: 'pointer' }}
            />
          </div>

          <div className="metrics" style={{ marginTop: '16px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '12px' }}>
            <div className="metric" style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px' }}>
              <div className="kicker" style={{ fontSize: '0.72rem' }}>ANNUAL PROTECTION COST</div>
              <div className="num" style={{ fontSize: '1.1rem', marginTop: '4px' }}>
                <AnimatedCurrency value={plan.estimatedCost} />
              </div>
            </div>

            <div className="metric" style={{ background: 'rgba(56, 189, 248, 0.08)', border: '1px solid rgba(56, 189, 248, 0.25)', padding: '12px', borderRadius: '8px' }}>
              <div className="kicker" style={{ color: '#38bdf8', fontSize: '0.72rem' }}>ESTIMATED RISK REDUCTION</div>
              <div className="num" style={{ fontSize: '1.15rem', color: '#38bdf8', fontWeight: 'bold', marginTop: '4px' }}>
                <AnimatedCurrency value={plan.riskReduction} />
              </div>
            </div>

            <div className="metric" style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '12px', borderRadius: '8px' }}>
              <div className="kicker" style={{ color: '#10b981', fontSize: '0.72rem' }}>NEW EXPECTED YEARLY LOSS</div>
              <div className="num" style={{ fontSize: '1.15rem', color: '#10b981', fontWeight: 'bold', marginTop: '4px' }}>
                <AnimatedCurrency value={plan.resultingEal} />
              </div>
            </div>

            <div className="metric" style={{ background: 'rgba(234, 179, 8, 0.08)', border: '1px solid rgba(234, 179, 8, 0.25)', padding: '12px', borderRadius: '8px' }}>
              <div className="kicker" style={{ color: '#eab308', fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>RETURN FROM INVESTMENT</span>
                <TechnicalTooltip termKey="ROSI" />
              </div>
              <div className="num" style={{ fontSize: '1.15rem', color: '#fde047', fontWeight: 'bold', marginTop: '4px' }}>
                {formatROSI(plan.rosi)}
              </div>
            </div>
          </div>

          <div style={{ marginTop: '16px' }}>
            <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              SELECTED PROTECTION SAFEGUARDS ({plan.selectedIds.length}):
            </div>
            <ul style={{ listStyle: 'none', padding: 0, margin: '0 0 16px 0', display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {plan.selectedIds.map((id) => {
                const c = controls.find((x) => x.id === id)
                return (
                  <li key={id} style={{ padding: '8px 12px', background: 'rgba(255,255,255,0.03)', borderRadius: '6px', fontSize: '0.85rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ color: '#e2e8f0', fontWeight: 500 }}>✓ {c?.name}</span>
                    <span style={{ color: '#38bdf8', fontFamily: 'IBM Plex Mono, monospace' }}>{c ? <AnimatedCurrency value={c.cost} /> : ''}</span>
                  </li>
                )
              })}
            </ul>
          </div>

          <button
            type="button"
            className="btn primary"
            onClick={handleApprove}
            style={{ width: '100%', padding: '12px', fontSize: '0.95rem', fontWeight: 600, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: '8px' }}
          >
            <span>Approve Protection Plan & Harden Live IT Model</span>
            <span>→</span>
          </button>
        </>
      )}

      <ExpandableTechnicalDetails termKey="ROSI" />
    </section>
  )
}

export function InvestmentCurve() {
  const { controls, baselineEal, budget } = useCyris()
  const max = Math.max(controls.reduce((s, c) => s + c.cost, 0), 1)
  const points = investmentCurve(controls, baselineEal, 8)
  const w = 420
  const h = 170
  const pad = 28
  const xs = points.map((p) => pad + (p.spend / max) * (w - pad * 2))
  const ys = points.map((p) => h - pad - (p.reduction / baselineEal) * (h - pad * 2))
  const d = xs.map((x, i) => `${i === 0 ? 'M' : 'L'} ${x} ${ys[i]}`).join(' ')
  const bx = pad + (budget / max) * (w - pad * 2)

  return (
    <section className="card">
      <div className="kicker" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span>DIMINISHING RETURNS CURVE</span>
        <TechnicalTooltip termKey="ROSI" />
      </div>
      <h2>SPEND VS RISK REDUCTION CURVE</h2>
      <svg viewBox={`0 0 ${w} ${h}`} width="100%" role="img" aria-label="Investment versus risk reduction">
        <path d={d} fill="none" stroke="#38bdf8" strokeWidth="2.5" />
        <line x1={bx} y1={pad} x2={bx} y2={h - pad} stroke="#c9a227" strokeDasharray="4 4" strokeWidth="2" />
        {xs.map((x, i) => (
          <circle key={points[i].spend} cx={x} cy={ys[i]} r="4" fill="#38bdf8" stroke="#0f172a" strokeWidth="2" />
        ))}
      </svg>
      <p className="muted" style={{ fontSize: '0.8rem', marginTop: '6px' }}>
        Gold vertical line marks your current budget ceiling. The curve shows diminishing returns as spend increases.
      </p>
    </section>
  )
}

export function RecentEvents() {
  const { telemetry } = useCyris()
  const navigate = useNavigate()
  const recent = [...telemetry].slice(-4).reverse()
  return (
    <section className="card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.8))' }}>
      <div className="kicker" style={{ color: '#38bdf8' }}>LIVE AUDIT STREAM</div>
      <h3 style={{ fontSize: '1.15rem', color: '#ffffff', margin: '4px 0 12px 0' }}>RECENT MATERIAL EVENTS</h3>
      {recent.length === 0 ? (
        <p className="panel-state">No security events recorded yet.</p>
      ) : (
        recent.map((e) => (
          <div key={e.id} className="contributor" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 0', borderBottom: '1px solid var(--border)' }}>
            <div>
              <div style={{ fontSize: '0.88rem', color: '#e2e8f0', fontWeight: 500 }}>{e.event}</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Source: {e.source}</div>
            </div>
            <div className="num" style={{ fontSize: '0.88rem', fontWeight: 600, color: e.ealImpact < 0 ? '#10b981' : '#f87171', fontFamily: 'IBM Plex Mono, monospace' }}>
              {e.ealImpact === 0 ? '—' : formatINRDelta(e.ealImpact)}
            </div>
          </div>
        ))
      )}
      <button type="button" className="btn" onClick={() => navigate('/telemetry')} style={{ marginTop: '14px', width: '100%', fontSize: '0.82rem', borderColor: '#38bdf8', color: '#38bdf8' }}>
        Open Live Activity Log →
      </button>
    </section>
  )
}
