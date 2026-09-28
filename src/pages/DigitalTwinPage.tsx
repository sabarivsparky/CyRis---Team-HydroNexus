import { AttackPathPanel } from '../components/DigitalTwin/AttackPathPanel'
import { GraphControls } from '../components/DigitalTwin/GraphControls'
import { NodeInspector } from '../components/DigitalTwin/NodeInspector'
import { RiskGraph } from '../components/DigitalTwin/RiskGraph'
import { TechnicalTooltip } from '../components/common/TechnicalDetails'
import { useCyris } from '../state/CyrisContext'

export function DigitalTwinPage() {
  const { twinPulse, lastApproval } = useCyris()

  return (
    <>
      <div className="row" style={{ justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>INTERACTIVE IT MODEL</span>
            <TechnicalTooltip termKey="digitalTwin" />
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: '#ef4444', fontWeight: 600, background: 'rgba(239, 68, 68, 0.1)', padding: '2px 8px', borderRadius: '12px', border: '1px solid rgba(239, 68, 68, 0.3)' }}>
              <span className="live-monitoring-dot" />
              <span>LIVE MONITORING</span>
            </div>
          </div>
          <h1 style={{ margin: '4px 0 0', fontSize: '1.5rem', color: '#ffffff' }}>
            LIVE MODEL OF YOUR IT ENVIRONMENT
          </h1>
          <p style={{ color: '#cbd5e1', fontSize: '0.9rem', margin: '4px 0 0 0' }}>
            An interactive model showing systems, connections, weaknesses and security protections.
          </p>
        </div>

        {lastApproval ? (
          <div className="severity low" style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid #10b981', color: '#10b981', padding: '6px 14px', borderRadius: '20px', fontWeight: 600, fontSize: '0.85rem' }}>
            ✓ IT Model Hardened · Control Active (Pulse {twinPulse})
          </div>
        ) : (
          <div className="muted" style={{ fontSize: '0.85rem' }}>
            Click any node to inspect shortest path to the Crown Jewels.
          </div>
        )}
      </div>

      <GraphControls />

      <p className="muted" style={{ margin: '4px 0 12px 0', fontSize: '0.82rem' }}>
        <strong>Legend:</strong> Critical System / Vault (Gold) · Security Protection (Green) · Employee Identity (Amber) · Server/Asset (Blue) · Vulnerability (Red).
      </p>

      <div className="graph-layout">
        <div>
          <RiskGraph />
          <div style={{ marginTop: 16 }}>
            <AttackPathPanel />
          </div>
        </div>
        <NodeInspector />
      </div>
    </>
  )
}
