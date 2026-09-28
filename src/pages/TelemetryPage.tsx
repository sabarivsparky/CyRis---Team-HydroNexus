import { TelemetryTimeline } from '../components/Telemetry/TelemetryTimeline'
import { PanelStatus } from '../components/common/PanelStatus'
import { TechnicalTooltip, ExpandableTechnicalDetails } from '../components/common/TechnicalDetails'
import { useCyris } from '../state/CyrisContext'

export function TelemetryPage() {
  const { panel, errorMessage, telemetry } = useCyris()

  return (
    <>
      <div>
        <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>CONTINUOUS SECURITY AUDIT STREAM</span>
          <TechnicalTooltip termKey="telemetry" />
        </div>
        <h1 style={{ margin: '4px 0 4px', fontSize: '1.5rem', color: '#ffffff' }}>
          LIVE SECURITY ACTIVITY & TELEMETRY LOG
        </h1>
        <p className="muted" style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
          Real-time event log capturing security changes, vulnerability discoveries, and control approvals with live financial EAL impact deltas.
        </p>
      </div>

      <section className="card">
        <PanelStatus
          state={panel}
          loading="Fetching live security activity stream..."
          empty="No security events yet. When the system detects a change, it will appear here with its estimated financial impact."
          error={errorMessage || 'Risk activity log couldn\'t be loaded.'}
        >
          <TelemetryTimeline events={telemetry} />
        </PanelStatus>
      </section>

      <ExpandableTechnicalDetails termKey="telemetry" />
    </>
  )
}
