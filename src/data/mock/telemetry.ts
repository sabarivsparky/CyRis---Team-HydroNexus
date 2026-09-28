import type { TelemetryEvent } from '../../types'

export const SEED_TELEMETRY: TelemetryEvent[] = [
  {
    id: 'tel-001',
    timestamp: '2026-09-24T04:31:00.000Z',
    event: 'Baseline platform EAL established from live twin',
    source: 'Digital Twin',
    severity: 'nominal',
    ealImpact: 0,
    status: 'nominal',
  },
  {
    id: 'tel-002',
    timestamp: '2026-09-24T04:34:00.000Z',
    event: 'Qualys sync: CVE-2026-3827 on mobile-banking-api-prod',
    source: 'Scanner',
    severity: 'high',
    ealImpact: 26_00_000,
    status: 'open',
  },
  {
    id: 'tel-003',
    timestamp: '2026-09-24T04:35:00.000Z',
    event: 'Lateral link to core transaction vault confirmed',
    source: 'Digital Twin',
    severity: 'critical',
    ealImpact: 2_70_00_000,
    status: 'open',
  },
  {
    id: 'tel-004',
    timestamp: '2026-09-24T04:42:15.000Z',
    event: 'Privileged account MFA still disabled (control gap)',
    source: 'SIEM',
    severity: 'high',
    ealImpact: 0,
    status: 'open',
  },
]
