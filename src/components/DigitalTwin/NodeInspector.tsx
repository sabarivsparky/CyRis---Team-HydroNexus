import { Link } from 'react-router-dom'
import { GRAPH_NODES } from '../../data/mock/attackGraph'
import { shortestPathToCrownJewel } from '../../data/mock/graphQueries'
import { useCyris } from '../../state/CyrisContext'
import { SeverityBadge } from '../common/SeverityBadge'
import { AnimatedCurrency } from '../common/AnimatedCurrency'
import { TechnicalTooltip } from '../common/TechnicalDetails'

export function NodeInspector() {
  const { selectedNodeId, approvedControlIds } = useCyris()
  const node = GRAPH_NODES.find((n) => n.id === selectedNodeId)

  if (!node) {
    return (
      <aside className="card inspector" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.8))' }}>
        <div className="kicker" style={{ color: '#38bdf8' }}>NODE INSPECTOR</div>
        <h3 style={{ fontSize: '1.1rem', color: '#ffffff', margin: '4px 0 8px 0' }}>INSPECT SYSTEM & ASSET</h3>
        <p className="muted" style={{ fontSize: '0.85rem' }}>
          Click any system node on the graph to inspect asset criticality, expected yearly loss contribution, and shortest attack path.
        </p>
      </aside>
    )
  }

  const path = shortestPathToCrownJewel(node.id)
  const connected = GRAPH_NODES.filter((n) => node.dependencies.includes(n.id) || n.dependencies.includes(node.id))
  const controlActive =
    (node.id === 'n-mfa' && approvedControlIds.includes('ctrl-mfa')) ||
    (node.id === 'n-seg' && approvedControlIds.includes('ctrl-seg')) ||
    ((node.id === 'n-vuln' || node.id === 'n-api') && approvedControlIds.includes('ctrl-cve')) ||
    (node.id === 'n-auth' && approvedControlIds.includes('ctrl-edr'))

  return (
    <aside className="card inspector" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.8))', border: '1px solid rgba(59, 130, 246, 0.3)' }}>
      <div className="kicker" style={{ color: '#38bdf8', textTransform: 'uppercase' }}>
        ASSET TYPE: {node.type}
      </div>
      <h2 style={{ fontSize: '1.3rem', color: '#ffffff', marginTop: '4px' }}>{node.name}</h2>

      <div style={{ margin: '8px 0' }}>
        <SeverityBadge level={node.criticality} />
      </div>

      <dl className="inspector-list" style={{ display: 'grid', gap: '10px', margin: '14px 0' }}>
        <div>
          <dt style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span>EXPECTED YEARLY LOSS CONTRIBUTION</span>
            <TechnicalTooltip termKey="EAL" />
          </dt>
          <dd className="num" style={{ fontSize: '1.3rem', color: '#f87171', fontWeight: 'bold' }}>
            <AnimatedCurrency value={node.ealContribution} />
          </dd>
        </div>

        <div>
          <dt style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>PROTECTION STATUS</dt>
          <dd style={{ color: controlActive ? '#10b981' : '#f59e0b', fontWeight: 600 }}>
            {controlActive ? '✓ ACTIVE — Protection Applied' : node.status}
          </dd>
        </div>

        <div>
          <dt style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>CONNECTED ASSETS ({connected.length})</dt>
          <dd style={{ color: '#cbd5e1', fontSize: '0.85rem' }}>
            {connected.map((c) => c.name).join(', ') || 'None recorded'}
          </dd>
        </div>

        <div>
          <dt style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>SHORTEST PATH TO VAULT ({path.nodes.length} HOPS)</dt>
          <dd style={{ color: '#e2e8f0', fontSize: '0.85rem', fontFamily: 'IBM Plex Mono, monospace' }}>
            {path.nodes.map((id) => GRAPH_NODES.find((n) => n.id === id)?.name).join(' → ')}
          </dd>
        </div>
      </dl>

      <Link
        to="/counterfactuals"
        className="btn primary"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '6px',
          width: '100%',
          padding: '10px',
          fontSize: '0.88rem',
          marginTop: '8px'
        }}
      >
        <span>Test Protection Counterfactual →</span>
      </Link>
    </aside>
  )
}
