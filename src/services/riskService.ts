import { USE_MOCK } from '../config/flags'
import { AGENT_RECORDS } from '../data/mock/agents'
import { ATTACK_PATHS, GRAPH_EDGES, GRAPH_NODES } from '../data/mock/attackGraph'
import { COMPLIANCE_ROWS } from '../data/mock/compliance'
import { CONTROLS } from '../data/mock/controls'
import { COUNTERFACTUALS } from '../data/mock/counterfactuals'
import { CONTRIBUTORS, INITIAL_TREND } from '../data/mock/dashboard'
import { SEED_TELEMETRY } from '../data/mock/telemetry'
import type {
  AgentRecord,
  AttackPath,
  ComplianceRow,
  CounterfactualScenario,
  GraphEdge,
  GraphNode,
  RiskContributor,
  SecurityControl,
  TelemetryEvent,
  TrendPoint,
} from '../types'
import { BASELINE_EAL, BASELINE_VAR95 } from '../utils/riskEngine'
import { fetchApi } from './apiClient'

const delay = (ms = 180) => new Promise((r) => setTimeout(r, ms))

interface BackendRiskSummary {
  eal_inr: number
  var95_inr: number
  var99_inr: number
  cvar95_inr: number
  as_of: string
}

interface BackendTwinGraphView {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

/** REAL DATA SERVICE — Toggles between live FastAPI backend and mock fallbacks per panel */
export const riskService = {
  async getDashboard(): Promise<{
    eal: number
    var95: number
    trend: TrendPoint[]
    contributors: RiskContributor[]
  }> {
    if (USE_MOCK.riskSummary && USE_MOCK.riskTrend && USE_MOCK.contributors) {
      await delay()
      return {
        eal: BASELINE_EAL,
        var95: BASELINE_VAR95,
        trend: INITIAL_TREND,
        contributors: CONTRIBUTORS,
      }
    }

    try {
      const [summary, trend, contributors] = await Promise.all([
        USE_MOCK.riskSummary
          ? Promise.resolve({ eal_inr: BASELINE_EAL, var95_inr: BASELINE_VAR95 })
          : fetchApi<BackendRiskSummary>('/risk/summary'),
        USE_MOCK.riskTrend
          ? Promise.resolve(INITIAL_TREND)
          : fetchApi<TrendPoint[]>('/risk/trend'),
        USE_MOCK.contributors
          ? Promise.resolve(CONTRIBUTORS)
          : fetchApi<RiskContributor[]>('/risk/contributors?level=asset&limit=10'),
      ])

      return {
        eal: summary.eal_inr,
        var95: summary.var95_inr,
        trend,
        contributors,
      }
    } catch (err) {
      console.warn('Backend API error, falling back to mock dashboard data:', err)
      return {
        eal: BASELINE_EAL,
        var95: BASELINE_VAR95,
        trend: INITIAL_TREND,
        contributors: CONTRIBUTORS,
      }
    }
  },

  async getAttackGraph(): Promise<{ nodes: GraphNode[]; edges: GraphEdge[]; paths: AttackPath[] }> {
    if (USE_MOCK.attackGraph) {
      await delay()
      return { nodes: GRAPH_NODES, edges: GRAPH_EDGES, paths: ATTACK_PATHS }
    }

    try {
      const [graphView, paths] = await Promise.all([
        fetchApi<BackendTwinGraphView>('/twin/graph?include_controls=true'),
        fetchApi<AttackPath[]>('/attack-paths?k=3'),
      ])

      return {
        nodes: graphView.nodes,
        edges: graphView.edges,
        paths,
      }
    } catch (err) {
      console.warn('Backend API error, falling back to mock attack graph data:', err)
      return { nodes: GRAPH_NODES, edges: GRAPH_EDGES, paths: ATTACK_PATHS }
    }
  },

  async getControls(): Promise<SecurityControl[]> {
    await delay()
    return CONTROLS
  },

  async getCounterfactuals(): Promise<CounterfactualScenario[]> {
    if (USE_MOCK.counterfactuals) {
      await delay()
      return COUNTERFACTUALS
    }

    try {
      return await fetchApi<CounterfactualScenario[]>('/counterfactuals')
    } catch (err) {
      console.warn('Backend API error, falling back to mock counterfactuals:', err)
      return COUNTERFACTUALS
    }
  },

  async getAgents(): Promise<AgentRecord[]> {
    await delay()
    return AGENT_RECORDS
  },

  async getCompliance(): Promise<ComplianceRow[]> {
    await delay()
    return COMPLIANCE_ROWS
  },

  async getTelemetry(): Promise<TelemetryEvent[]> {
    await delay()
    return SEED_TELEMETRY
  },
}
