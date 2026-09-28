import { COUNTERFACTUALS } from '../data/mock/counterfactuals'
import { CounterfactualCard } from '../components/Counterfactual/CounterfactualCard'
import { TechnicalTooltip } from '../components/common/TechnicalDetails'
import { useCyris } from '../state/CyrisContext'

export function CounterfactualsPage() {
  const { lastApproval } = useCyris()

  return (
    <>
      <div>
        <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>PROTECTION SCENARIO SIMULATOR</span>
          <TechnicalTooltip termKey="counterfactual" />
        </div>
        <h1 style={{ margin: '4px 0 4px', fontSize: '1.5rem', color: '#ffffff' }}>
          WHAT-IF PROTECTION SIMULATOR
        </h1>
        <p className="muted" style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
          Test individual security safeguards to compare expected financial risk reduction against installation costs before committing capital.
        </p>
      </div>

      {lastApproval ? (
        <div className="card" style={{ borderColor: '#10b981', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', padding: '12px 16px', borderRadius: '8px' }}>
          ✓ <strong>Protection Approved:</strong> IT Model hardened. Executive Dashboard EAL and risk trend chart updated in real-time.
        </div>
      ) : null}

      <div className="grid-2">
        {COUNTERFACTUALS.map((cf) => (
          <CounterfactualCard key={cf.id} controlId={cf.controlId} />
        ))}
      </div>
    </>
  )
}
