import type { RiskContributor, TrendPoint } from '../../types'
import { BASELINE_EAL } from '../../utils/riskEngine'

export const INITIAL_TREND: TrendPoint[] = [
  { label: 'Apr', eal: 1_85_00_000 },
  { label: 'May', eal: 2_10_00_000 },
  { label: 'Jun', eal: 2_05_00_000 },
  { label: 'Jul', eal: 2_40_00_000 },
  { label: 'Aug', eal: 3_10_00_000 },
  { label: 'Sep', eal: BASELINE_EAL },
]

export const CONTRIBUTORS: RiskContributor[] = [
  {
    id: 'c1',
    name: 'Privileged identity hop to vault',
    pathId: 'path-7',
    eal: 2_70_00_000,
    share: 0.64,
    severity: 'critical',
  },
  {
    id: 'c2',
    name: 'Unpatched API gateway (CVE-2026-3827)',
    pathId: 'path-7',
    eal: 42_30_000,
    share: 0.1,
    severity: 'high',
  },
  {
    id: 'c3',
    name: 'Auth service token reuse',
    pathId: 'path-3',
    eal: 68_00_000,
    share: 0.16,
    severity: 'high',
  },
  {
    id: 'c4',
    name: 'EDR coverage gap on mid-tier',
    pathId: 'path-3',
    eal: 39_70_000,
    share: 0.1,
    severity: 'medium',
  },
]
