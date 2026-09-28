import { formatINR, formatPercent } from '../../utils/formatINR'
import type { AgentRecord } from '../../types'
import { Link } from 'react-router-dom'

export function RedAgentFinding({ record }: { record: AgentRecord }) {
  const { red } = record
  return (
    <section className="card" style={{ borderColor: 'rgba(239, 68, 68, 0.4)', background: 'linear-gradient(180deg, rgba(239, 68, 68, 0.05) 0%, rgba(15, 23, 42, 0.6) 100%)' }}>
      <div className="kicker" style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444', boxShadow: '0 0 8px #ef4444' }} />
        RED AGENT · EXPLOIT ANALYST
      </div>
      <h2 style={{ marginTop: '4px' }}>Finding</h2>
      <p style={{ color: '#e2e8f0', lineHeight: 1.6 }}>{red.finding}</p>
      
      <dl className="inspector" style={{ marginTop: '16px' }}>
        <dt>Attack vector</dt>
        <dd style={{ color: '#fca5a5' }}>{red.attackVector}</dd>
        <dt>Affected asset</dt>
        <dd>{red.affectedAsset}</dd>
        <dt>Estimated impact</dt>
        <dd className="num" style={{ color: '#ef4444', fontSize: '1.25rem', fontWeight: 'bold' }}>{formatINR(red.estimatedImpact)}</dd>
      </dl>

      <h3 style={{ marginTop: '20px', fontSize: '0.9rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Evidence Chain</h3>
      <ul className="evidence" style={{ listStyle: 'none', paddingLeft: 0 }}>
        {red.evidence.map((e) => (
          <li key={e.id} style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.08)', borderRadius: '6px', marginBottom: '6px', borderLeft: '3px solid #ef4444', fontSize: '0.85rem' }}>
            <strong style={{ color: '#f87171' }}>{e.label}</strong> · <span style={{ opacity: 0.8 }}>{e.source}</span>: {e.detail}
          </li>
        ))}
      </ul>
    </section>
  )
}

export function BlueAgentResponse({ record }: { record: AgentRecord }) {
  const { blue } = record
  return (
    <section className="card" style={{ borderColor: 'rgba(59, 130, 246, 0.4)', background: 'linear-gradient(180deg, rgba(59, 130, 246, 0.05) 0%, rgba(15, 23, 42, 0.6) 100%)' }}>
      <div className="kicker" style={{ color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6', boxShadow: '0 0 8px #3b82f6' }} />
        BLUE AGENT · CONTROL DEFENDER
      </div>
      <h2 style={{ marginTop: '4px' }}>Existing control</h2>
      <p style={{ color: '#e2e8f0', lineHeight: 1.6 }}>{blue.existingControl}</p>

      <dl className="inspector" style={{ marginTop: '16px' }}>
        <dt>Mitigation</dt>
        <dd style={{ color: '#93c5fd' }}>{blue.mitigation}</dd>
        <dt>Residual risk</dt>
        <dd>{blue.residualRisk}</dd>
        <dt>Counterargument</dt>
        <dd style={{ fontStyle: 'italic', color: '#cbd5e1' }}>"{blue.counterargument}"</dd>
      </dl>

      <h3 style={{ marginTop: '20px', fontSize: '0.9rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Control Telemetry</h3>
      <ul className="evidence" style={{ listStyle: 'none', paddingLeft: 0 }}>
        {blue.evidence.map((e) => (
          <li key={e.id} style={{ padding: '8px 12px', background: 'rgba(59, 130, 246, 0.08)', borderRadius: '6px', marginBottom: '6px', borderLeft: '3px solid #3b82f6', fontSize: '0.85rem' }}>
            <strong style={{ color: '#60a5fa' }}>{e.label}</strong> · <span style={{ opacity: 0.8 }}>{e.source}</span>: {e.detail}
          </li>
        ))}
      </ul>
    </section>
  )
}

export function JudgeDecision({ record }: { record: AgentRecord }) {
  const { judge } = record
  return (
    <section className="card judge" style={{ borderColor: 'rgba(234, 179, 8, 0.5)', background: 'linear-gradient(180deg, rgba(234, 179, 8, 0.08) 0%, rgba(15, 23, 42, 0.9) 100%)', boxShadow: '0 8px 32px rgba(234, 179, 8, 0.1)' }}>
      <div className="kicker" style={{ color: '#eab308', display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span style={{ display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', background: '#eab308', boxShadow: '0 0 10px #eab308' }} />
        JUDGE AGENT · QUANTIFICATION & ARBITRATION
      </div>
      <h2 style={{ marginTop: '4px' }}>Synthesized finding</h2>
      <p style={{ fontSize: '1.05rem', color: '#fef08a', lineHeight: 1.6, fontWeight: 500 }}>{judge.synthesizedFinding}</p>

      <div className="metrics" style={{ margin: '20px 0', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))' }}>
        <div className="metric">
          <div className="kicker">Financial impact</div>
          <div className="num" style={{ color: '#ef4444' }}>{formatINR(judge.financialImpact)}</div>
        </div>
        <div className="metric">
          <div className="kicker">Confidence</div>
          <div className="num" style={{ color: '#3b82f6' }}>{formatPercent(judge.confidence)}</div>
        </div>
        <div className="metric">
          <div className="kicker">Evidence state</div>
          <div style={{ fontWeight: 600, color: '#10b981', marginTop: '4px' }}>{judge.evidenceState}</div>
        </div>
      </div>

      <div style={{ padding: '16px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid rgba(234, 179, 8, 0.2)', marginBottom: '20px' }}>
        <div className="kicker" style={{ color: '#eab308', marginBottom: '4px' }}>Recommended action</div>
        <div style={{ color: '#e2e8f0', lineHeight: 1.5 }}>{judge.recommendedAction}</div>
      </div>

      <Link to="/counterfactuals" className="btn primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', fontSize: '0.95rem' }}>
        <span>Open recommended counterfactual</span>
        <span>→</span>
      </Link>
    </section>
  )
}
