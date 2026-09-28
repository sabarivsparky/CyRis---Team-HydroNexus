import { TelemetryEventRow } from './TelemetryEvent'
import type { TelemetryEvent } from '../../types'

export function TelemetryTimeline({ events }: { events: TelemetryEvent[] }) {
  if (events.length === 0) {
    return (
      <p className="panel-state">
        No telemetry events yet. Events will appear when the Digital Twin receives a state change.
      </p>
    )
  }
  const ordered = [...events].sort((a, b) => +new Date(b.timestamp) - +new Date(a.timestamp))
  return (
    <div className="timeline">
      {ordered.map((e) => (
        <TelemetryEventRow key={e.id} item={e} />
      ))}
    </div>
  )
}
