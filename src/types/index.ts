export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'nominal'

export type NodeType = 'asset' | 'identity' | 'control' | 'vulnerability' | 'crown-jewel' | 'external'

export type ControlStatus = 'absent' | 'degraded' | 'active' | 'proposed'

export type ProofStatus = 'verified' | 'unverified' | 'pending'

export type Framework = 'ISO 27001' | 'NIST CSF' | 'RBI CSF' | 'SEBI CSCRF'

export type TelemetrySource =
  | 'Control Change'
  | 'Scanner'
  | 'SIEM'
  | 'Digital Twin'
  | 'Budget Optimizer'
  | 'Agent Judge'
  | 'Ingestion'

export type PanelState = 'loading' | 'empty' | 'error' | 'success'

export interface GraphNode {
  id: string
  name: string
  type: NodeType
  criticality: Severity
  ealContribution: number
  status: ControlStatus | 'exposed' | 'monitored' | 'hardened'
  x: number
  y: number
  dependencies: string[]
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  kind: 'attack' | 'control' | 'identity'
  label: string
}

export interface AttackPath {
  id: string
  name: string
  nodeIds: string[]
  edgeIds: string[]
  ealContribution: number
  hopsToCrownJewel: number
}

export interface SecurityControl {
  id: string
  name: string
  description: string
  cost: number
  standaloneReduction: number
  blocksNodeIds: string[]
  relatedPathId: string
  frameworkHints: Framework[]
}

export interface CounterfactualScenario {
  id: string
  controlId: string
  title: string
  proposedAction: string
}

export interface TelemetryEvent {
  id: string
  timestamp: string
  event: string
  source: TelemetrySource
  severity: Severity
  ealImpact: number
  status: 'open' | 'absorbed' | 'approved' | 'nominal'
}

export interface RiskContributor {
  id: string
  name: string
  pathId: string
  eal: number
  share: number
  severity: Severity
}

export interface TrendPoint {
  label: string
  eal: number
}

export interface AgentEvidence {
  id: string
  label: string
  source: string
  detail: string
}

export interface RedFinding {
  finding: string
  attackVector: string
  affectedAsset: string
  estimatedImpact: number
  evidence: AgentEvidence[]
}

export interface BlueResponse {
  existingControl: string
  mitigation: string
  residualRisk: string
  counterargument: string
  evidence: AgentEvidence[]
}

export interface JudgeDecision {
  synthesizedFinding: string
  financialImpact: number
  confidence: number
  evidenceState: 'partial' | 'grounded' | 'contested'
  recommendedAction: string
  recommendedControlId: string
}

export interface AgentRecord {
  id: string
  title: string
  relatedControlId: string
  red: RedFinding
  blue: BlueResponse
  judge: JudgeDecision
}

export interface ComplianceRow {
  id: string
  finding: string
  control: string
  framework: Framework
  clause: string
  status: 'mapped' | 'gap' | 'in-progress'
  evidence: string
  proof: ProofStatus
  proofRef: string
}

export interface OptimizationResult {
  selectedIds: string[]
  estimatedCost: number
  riskReduction: number
  resultingEal: number
  rosi: number
  remainingBudget: number
}

export interface DashboardSnapshot {
  eal: number
  var95: number
  posture: Severity
  trend: TrendPoint[]
  contributors: RiskContributor[]
}
