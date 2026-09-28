import { formatINRDelta, formatTimestamp } from '../../utils/formatINR'
import { SeverityBadge } from '../common/SeverityBadge'
import type { TelemetryEvent } from '../../types'

export function TelemetryEventRow({ item }: { item: TelemetryEvent }) {
  const isPositive = item.ealImpact > 0
  const isNegative = item.ealImpact < 0

  return (
    <article
      className={`tel-item ${item.status}`}
      style={{
        display: 'grid',
        gridTemplateColumns: '120px 1fr auto',
        alignItems: 'center',
        gap: '16px',
        padding: '12px 16px',
        background: 'rgba(255, 255, 255, 0.02)',
        border: '1px solid var(--border)',
        borderRadius: '8px',
        marginBottom: '10px',
        transition: 'all 0.2s ease'
      }}
    >
      <div className="num" style={{ fontSize: '0.78rem', color: '#94a3b8', fontFamily: 'IBM Plex Mono, monospace' }}>
        {formatTimestamp(item.timestamp)}
      </div>

      <div>
        <div style={{ fontWeight: 600, color: '#e2e8f0', fontSize: '0.92rem' }}>{item.event}</div>
        <div className="muted" style={{ fontSize: '0.8rem', marginTop: '2px', display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span>Source: <strong style={{ color: '#cbd5e1' }}>{item.source}</strong></span>
          <span>•</span>
          <span style={{ textTransform: 'capitalize', color: item.status === 'absorbed' || item.status === 'approved' ? '#10b981' : '#f59e0b' }}>
            {item.status}
          </span>
        </div>
      </div>

      <div style={{ textAlign: 'right', display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
        <SeverityBadge level={item.severity} />
        <div
          className="num"
          style={{
            fontSize: '0.85rem',
            fontWeight: 600,
            fontFamily: 'IBM Plex Mono, monospace',
            color: isPositive ? '#ef4444' : isNegative ? '#10b981' : '#94a3b8'
          }}
        >
          {item.ealImpact === 0 ? 'EAL —' : `EAL ${formatINRDelta(item.ealImpact)}`}
        </div>
      </div>
    </article>
  )
}
