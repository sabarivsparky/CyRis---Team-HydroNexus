import type { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useCyris } from '../state/CyrisContext'
import { AnimatedCurrency } from '../components/common/AnimatedCurrency'
import { TechnicalTooltip } from '../components/common/TechnicalDetails'
import { DemoModeButton } from '../components/common/DemoMode'

const LINKS = [
  { to: '/', label: 'Executive Dashboard', technical: 'EAL & VaR' },
  { to: '/twin', label: 'Live IT Model', technical: 'Digital Twin' },
  { to: '/counterfactuals', label: 'Protection Simulator', technical: 'Counterfactuals' },
  { to: '/agents', label: 'Risk Decision Agents', technical: 'Red / Blue / Judge' },
  { to: '/compliance', label: 'Regulatory Audit Ledger', technical: 'Compliance' },
  { to: '/telemetry', label: 'Live Activity Log', technical: 'Telemetry' },
]

export function AppShell({ children }: { children: ReactNode }) {
  const { displayEal, posture } = useCyris()

  return (
    <div className="shell">
      <aside className="rail">
        <div className="brand">
          <strong>CYRIS</strong>
          <span>Cyber Risk Information System</span>
          <span style={{ color: '#38bdf8', fontWeight: 600 }}>SIH26105 · DEMO</span>
        </div>

        <nav className="nav" aria-label="Primary">
          {LINKS.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.to === '/'}>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontWeight: 500 }}>{l.label}</span>
                <span style={{ fontSize: '0.72rem', color: '#94a3b8', fontFamily: 'IBM Plex Mono, monospace' }}>{l.technical}</span>
              </div>
            </NavLink>
          ))}
        </nav>

        <div className="rail-eal" style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '8px', padding: '12px' }}>
          <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span>EXPECTED YEARLY LOSS</span>
            <TechnicalTooltip termKey="EAL" />
          </div>
          <div className="num" style={{ fontSize: '1.25rem', color: '#ffffff', fontWeight: 'bold', marginTop: '4px' }}>
            <AnimatedCurrency value={displayEal} />
          </div>
          <div className="muted" style={{ fontSize: '0.75rem', marginTop: '6px', color: '#10b981', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981' }} />
            Risk Posture: <strong style={{ color: '#ffffff' }}>{posture}</strong>
          </div>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div className="kicker" style={{ color: '#38bdf8' }}>BOARDROOM CYBER RISK DECISION TERMINAL</div>
            <div style={{ color: '#e2e8f0', fontSize: '0.9rem' }}>Quantifying cyber exposure in rupees — clear for executive leadership.</div>
          </div>

          <DemoModeButton />
        </header>

        <main className="page">{children}</main>
      </div>
    </div>
  )
}
