import type { Severity } from '../../types'

const LABELS: Record<Severity, string> = {
  critical: 'Critical',
  high: 'High',
  medium: 'Medium',
  low: 'Low',
  nominal: 'Nominal',
}

export function SeverityBadge({ level }: { level: Severity }) {
  return (
    <span className={`severity ${level}`}>
      <span className="mark" aria-hidden="true" />
      {LABELS[level]}
    </span>
  )
}
