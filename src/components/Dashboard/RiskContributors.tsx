import { useNavigate } from 'react-router-dom'
import { formatPercent } from '../../utils/formatINR'
import { SeverityBadge } from '../common/SeverityBadge'
import { AnimatedCurrency } from '../common/AnimatedCurrency'
import { TechnicalTooltip } from '../common/TechnicalDetails'
import type { RiskContributor } from '../../types'
import { useCyris } from '../../state/CyrisContext'

export function RiskContributors({ items }: { items: RiskContributor[] }) {
  const { highlightPath } = useCyris()
  const navigate = useNavigate()

  if (items.length === 0) {
    return <p className="panel-state">No material risk contributors identified on the current live model.</p>
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>PRIMARY EXPOSURE DRIVERS</span>
            <TechnicalTooltip termKey="riskContributors" />
          </div>
          <h3 style={{ fontSize: '1.15rem', color: '#ffffff', margin: '2px 0 0 0' }}>
            WHAT IS DRIVING YOUR CYBER RISK?
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', margin: '2px 0 0 0' }}>
            These systems and weaknesses contribute the most to your total estimated financial exposure.
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {items.map((c, index) => (
          <div
            key={c.id}
            className="contributor"
            style={{
              padding: '14px 16px',
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              display: 'grid',
              gridTemplateColumns: '1fr auto',
              alignItems: 'center',
              gap: '16px',
              transition: 'all 0.2s ease',
              animation: `fadeIn 0.3s ease-out ${index * 0.08}s both`
            }}
          >
            <div>
              <div className="row" style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 'bold', color: '#38bdf8', fontFamily: 'IBM Plex Mono, monospace' }}>
                  #{index + 1}
                </span>
                <strong style={{ fontSize: '0.98rem', color: '#e2e8f0' }}>{c.name}</strong>
                <SeverityBadge level={c.severity} />
              </div>

              {/* Share Bar */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div className="bar" aria-hidden="true" style={{ flex: 1, height: '6px', background: 'rgba(255, 255, 255, 0.1)', borderRadius: '3px', overflow: 'hidden' }}>
                  <span style={{ display: 'block', height: '100%', width: formatPercent(c.share), background: 'linear-gradient(90deg, #38bdf8, #ef4444)', transition: 'width 0.6s ease' }} />
                </div>
                <span style={{ fontSize: '0.78rem', color: '#94a3b8', fontFamily: 'IBM Plex Mono, monospace', minWidth: '45px' }}>
                  {formatPercent(c.share)}
                </span>
              </div>
            </div>

            <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '6px' }}>
              <div className="num" style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#f87171' }}>
                <AnimatedCurrency value={c.eal} />
              </div>

              <button
                type="button"
                className="btn"
                style={{
                  fontSize: '0.8rem',
                  padding: '4px 10px',
                  borderColor: 'rgba(56, 189, 248, 0.4)',
                  color: '#38bdf8'
                }}
                onClick={() => {
                  highlightPath(c.pathId)
                  navigate('/twin')
                }}
              >
                See How Attack Could Spread →
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
