import type { CounterfactualScenario } from '../../types'

export const COUNTERFACTUALS: CounterfactualScenario[] = [
  {
    id: 'cf-mfa',
    controlId: 'ctrl-mfa',
    title: 'Break the identity hop',
    proposedAction: 'Enable MFA for privileged accounts',
  },
  {
    id: 'cf-cve',
    controlId: 'ctrl-cve',
    title: 'Close the edge exploit',
    proposedAction: 'Remediate CVE-2026-3827 on the API gateway',
  },
  {
    id: 'cf-edr',
    controlId: 'ctrl-edr',
    title: 'Contain mid-tier hosts',
    proposedAction: 'Expand EDR host agent coverage',
  },
  {
    id: 'cf-seg',
    controlId: 'ctrl-seg',
    title: 'Cut east-west traversal',
    proposedAction: 'Apply network subnet segmentation on Subnet B',
  },
]
