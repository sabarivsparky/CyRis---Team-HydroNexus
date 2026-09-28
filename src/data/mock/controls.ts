import type { SecurityControl } from '../../types'

export const CONTROLS: SecurityControl[] = [
  {
    id: 'ctrl-mfa',
    name: 'Phishing-resistant MFA',
    description: 'Enable phishing-resistant MFA for privileged accounts on the identity hop to the transaction vault.',
    cost: 18_00_000,
    standaloneReduction: 85_00_000,
    blocksNodeIds: ['n-identity'],
    relatedPathId: 'path-7',
    frameworkHints: ['ISO 27001', 'NIST CSF', 'RBI CSF', 'SEBI CSCRF'],
  },
  {
    id: 'ctrl-cve',
    name: 'Remediate critical API CVEs',
    description: 'Patch CVE-2026-3827 on the mobile banking API edge node.',
    cost: 8_00_000,
    standaloneReduction: 90_00_000,
    blocksNodeIds: ['n-vuln', 'n-api'],
    relatedPathId: 'path-7',
    frameworkHints: ['ISO 27001', 'NIST CSF'],
  },
  {
    id: 'ctrl-edr',
    name: 'Expand EDR host coverage',
    description: 'Extend EDR behavioral isolation to the authentication microservice hosts.',
    cost: 12_00_000,
    standaloneReduction: 70_00_000,
    blocksNodeIds: ['n-auth'],
    relatedPathId: 'path-7',
    frameworkHints: ['NIST CSF', 'RBI CSF'],
  },
  {
    id: 'ctrl-seg',
    name: 'Network subnet segmentation',
    description: 'Segment Subnet B so the privileged principal cannot traverse to the crown-jewel vault.',
    cost: 25_00_000,
    standaloneReduction: 1_20_00_000,
    blocksNodeIds: ['n-identity', 'n-jewel'],
    relatedPathId: 'path-7',
    frameworkHints: ['SEBI CSCRF', 'RBI CSF'],
  },
]
