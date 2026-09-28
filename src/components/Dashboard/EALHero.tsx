import { SeverityBadge } from '../common/SeverityBadge'
import { AnimatedCurrency } from '../common/AnimatedCurrency'
import { TechnicalTooltip, ExpandableTechnicalDetails } from '../common/TechnicalDetails'
import type { Severity } from '../../types'

export function EALHero({
  eal,
  var95,
  posture,
}: {
  eal: number
  var95: number
  posture: Severity
}) {
  return (
    <section className="card hero-card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.8))', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div className="kicker" style={{ color: '#38bdf8', fontSize: '0.8rem', letterSpacing: '0.08em' }}>
            ORGANIZATION FINANCIAL EXPOSURE
          </div>

          <h2 style={{ fontSize: '1.4rem', marginTop: '4px', color: '#ffffff' }}>
            YOUR CURRENT CYBER RISK
          </h2>

          <div style={{ margin: '12px 0 6px 0' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#f87171', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
              <AnimatedCurrency value={eal} />
            </div>
            <p style={{ color: '#cbd5e1', fontSize: '0.9rem', marginTop: '6px', maxWidth: '520px', lineHeight: 1.5 }}>
              Estimated amount the organization could lose from cyber incidents over one year.
            </p>
          </div>
        </div>

        {/* Worst-Case Loss (VaR 95) & Posture Badge */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Enterprise Risk Posture:</span>
            <SeverityBadge level={posture} />
          </div>

          <div
            style={{
              padding: '12px 18px',
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.25)',
              borderRadius: '8px',
              textAlign: 'right'
            }}
          >
            <div style={{ fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end' }}>
              <span>WORST-CASE LOSS ESTIMATE</span>
              <TechnicalTooltip termKey="VaR95" />
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: '#ef4444', marginTop: '2px' }}>
              <AnimatedCurrency value={var95} />
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>
              Estimated 95% scenario limit
            </div>
          </div>
        </div>
      </div>

      {/* Technical Details Progressive Disclosure */}
      <ExpandableTechnicalDetails termKey="EAL" />
    </section>
  )
}
