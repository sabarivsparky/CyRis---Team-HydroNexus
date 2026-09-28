import { ATTACK_PATHS } from '../../data/mock/attackGraph'
import { GRAPH_NODES } from '../../data/mock/attackGraph'
import { useCyris } from '../../state/CyrisContext'
import { AnimatedCurrency } from '../common/AnimatedCurrency'
import { TechnicalTooltip, ExpandableTechnicalDetails } from '../common/TechnicalDetails'

export function AttackPathPanel() {
  const { activePathNodeIds, highlightPath } = useCyris()
  const path =
    ATTACK_PATHS.find((p) => p.nodeIds.every((id) => activePathNodeIds.includes(id))) ?? ATTACK_PATHS[0]

  const nodeNames = path.nodeIds.map((id) => GRAPH_NODES.find((n) => n.id === id)?.name ?? id)

  return (
    <section className="card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.8))', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
      <div className="kicker" style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span>ACTIVE EXPLOIT ROUTE</span>
        <TechnicalTooltip termKey="attackPath" />
      </div>

      <h3 style={{ fontSize: '1.2rem', color: '#ffffff', marginTop: '4px' }}>
        HOW COULD AN ATTACKER REACH THE CRITICAL SYSTEM?
      </h3>

      <div style={{ margin: '10px 0 14px 0', padding: '10px 14px', background: 'rgba(239, 68, 68, 0.08)', borderRadius: '6px', borderLeft: '3px solid #ef4444' }}>
        <div style={{ fontSize: '0.75rem', color: '#fca5a5', textTransform: 'uppercase' }}>ESTIMATED FINANCIAL EXPOSURE FROM THIS ROUTE</div>
        <div style={{ fontSize: '1.3rem', fontWeight: 'bold', color: '#ef4444', marginTop: '2px' }}>
          <AnimatedCurrency value={path.ealContribution} />
        </div>
      </div>

      <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '12px' }}>
        <strong>Step-by-step attack progression ({path.hopsToCrownJewel} steps):</strong>
      </div>

      <ol style={{ paddingLeft: '20px', margin: '0 0 16px 0', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.88rem', color: '#e2e8f0' }}>
        {nodeNames.map((name, i) => (
          <li key={i} style={{ padding: '6px 10px', background: 'rgba(255,255,255,0.03)', borderRadius: '4px', border: '1px solid var(--border)' }}>
            <span style={{ color: i === nodeNames.length - 1 ? '#eab308' : '#38bdf8', fontWeight: 600 }}>
              {i === 0 ? '🏁 Entry Point: ' : i === nodeNames.length - 1 ? '👑 Target (Crown Jewel): ' : `Step ${i + 1}: `}
            </span>
            <span>{name}</span>
          </li>
        ))}
      </ol>

      <button
        type="button"
        className="btn"
        onClick={() => highlightPath(path.id)}
        style={{ width: '100%', padding: '8px', borderColor: '#ef4444', color: '#ef4444', fontSize: '0.85rem' }}
      >
        Highlight Route on Live IT Model
      </button>

      <ExpandableTechnicalDetails termKey="attackPath" />
    </section>
  )
}
