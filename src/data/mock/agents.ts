import type { AgentRecord } from '../../types'

export const AGENT_RECORDS: AgentRecord[] = [
  {
    id: 'debate-mfa',
    title: 'Privileged path to transaction vault',
    relatedControlId: 'ctrl-mfa',
    red: {
      finding:
        'CVE-2026-3827 establishes an open exploit path from the public API container into the privileged backup account service principal.',
      attackVector: 'Public API RCE → env-var pivot → Kubernetes SA token hijack → AD principal → vault',
      affectedAsset: 'Core transaction vault (crown jewel)',
      estimatedImpact: 2_70_00_000,
      evidence: [
        {
          id: 'ev-r1',
          label: 'Qualys finding',
          source: 'Qualys VMDR',
          detail: 'CVE-2026-3827 CVSS 9.8 on mobile-banking-api-prod, unauthenticated RCE.',
        },
        {
          id: 'ev-r2',
          label: 'Graph path',
          source: 'Digital Twin / Neo4j',
          detail: 'Shortest path to crown jewel is 4 hops; identity node betweenness is a structural bridge.',
        },
      ],
    },
    blue: {
      existingControl: 'CrowdStrike Falcon behavioral isolation on downstream hosts; Okta SSO on human users.',
      mitigation: 'Host isolation can interrupt post-exploit tooling, but does not bind the service principal.',
      residualRisk: 'Privileged non-human identity still authenticates with a static secret. Residual EAL remains material.',
      counterargument:
        'CrowdStrike Falcon is confirmed active on the auth hosts, and micro-segmentation blocks some front-end cluster traffic. The identity hop is not covered.',
      evidence: [
        {
          id: 'ev-b1',
          label: 'EDR health',
          source: 'CrowdStrike',
          detail: 'Falcon sensor healthy on auth-ms-a/b. Coverage gap on privileged jump path.',
        },
        {
          id: 'ev-b2',
          label: 'IAM config',
          source: 'Okta / AD',
          detail: 'Human workforce MFA on. Service principal MFA: ABSENT (DEMO DATA).',
        },
      ],
    },
    judge: {
      synthesizedFinding:
        'The exploit is real and the twin confirms a live lateral path. Existing EDR reduces post-exploit dwell, but does not break Step 3 (privileged identity). Residual sub-graph EAL remains dominated by the MFA gap.',
      financialImpact: 2_70_00_000,
      confidence: 0.86,
      evidenceState: 'grounded',
      recommendedAction: 'Enable phishing-resistant MFA for privileged accounts. Human approval required before production merge.',
      recommendedControlId: 'ctrl-mfa',
    },
  },
]
