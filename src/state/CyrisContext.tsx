/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react'
import { CONTROLS } from '../data/mock/controls'
import { ATTACK_PATHS } from '../data/mock/attackGraph'
import { COMPLIANCE_ROWS } from '../data/mock/compliance'
import { CONTRIBUTORS, INITIAL_TREND } from '../data/mock/dashboard'
import { shortestPathToCrownJewel } from '../data/mock/graphQueries'
import { SEED_TELEMETRY } from '../data/mock/telemetry'
import { riskService } from '../services/riskService'
import type {
  ComplianceRow,
  PanelState,
  SecurityControl,
  Severity,
  TelemetryEvent,
  TrendPoint,
} from '../types'
import {
  BASELINE_EAL,
  BASELINE_VAR95,
  calculateEAL,
  calculateVaR,
  optimizeBudget,
  postureFromEal,
  simulateControlChange,
} from '../utils/riskEngine'

const DEFAULT_BUDGET = 50_00_000

interface CyrisState {
  panel: PanelState
  errorMessage: string
  baselineEal: number
  currentEal: number
  displayEal: number
  var95: number
  budget: number
  selectedControlIds: string[]
  approvedControlIds: string[]
  selectedNodeId: string | null
  activePathNodeIds: string[]
  activePathEdgeIds: string[]
  telemetry: TelemetryEvent[]
  compliance: ComplianceRow[]
  trend: TrendPoint[]
  lastApproval: string | null
  twinPulse: number
}

interface CyrisContextValue extends CyrisState {
  controls: SecurityControl[]
  posture: Severity
  contributors: typeof CONTRIBUTORS
  setBudget: (n: number) => void
  applyBudgetPlan: () => void
  selectNode: (id: string | null) => void
  highlightPath: (pathId: string) => void
  approveControl: (controlId: string) => void
  retryLoad: () => void
}

const CyrisContext = createContext<CyrisContextValue | null>(null)

function applyControlToCompliance(rows: ComplianceRow[], control: SecurityControl): ComplianceRow[] {
  const related = new Set<string>()
  if (control.id === 'ctrl-mfa') {
    related.add('cmp-2')
    related.add('cmp-3')
    related.add('cmp-4')
  }
  if (control.id === 'ctrl-cve' || control.id === 'ctrl-seg') related.add('cmp-1')
  if (control.id === 'ctrl-edr') related.add('cmp-5')
  return rows.map((row) => {
    if (!related.has(row.id)) return row
    return {
      ...row,
      status: 'mapped',
      proof: 'verified',
      evidence: `Approved ${control.name}. Twin updated. ${row.evidence}`,
      proofRef: `dilithium:${row.id}:verified`,
    }
  })
}

export function CyrisProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<CyrisState>({
    panel: 'loading',
    errorMessage: '',
    baselineEal: BASELINE_EAL,
    currentEal: BASELINE_EAL,
    displayEal: BASELINE_EAL,
    var95: BASELINE_VAR95,
    budget: DEFAULT_BUDGET,
    selectedControlIds: [],
    approvedControlIds: [],
    selectedNodeId: null,
    activePathNodeIds: ATTACK_PATHS[0].nodeIds,
    activePathEdgeIds: ATTACK_PATHS[0].edgeIds,
    telemetry: SEED_TELEMETRY,
    compliance: COMPLIANCE_ROWS,
    trend: INITIAL_TREND,
    lastApproval: null,
    twinPulse: 0,
  })

  const load = useCallback(async () => {
    setState((s) => ({ ...s, panel: 'loading' }))
    try {
      const dash = await riskService.getDashboard()
      const tel = await riskService.getTelemetry()
      const cmp = await riskService.getCompliance()
      setState((s) => {
        if (s.twinPulse > 0 || s.approvedControlIds.length > 0) {
          return { ...s, panel: 'success', errorMessage: '' }
        }
        return {
          ...s,
          panel: 'success',
          errorMessage: '',
          baselineEal: dash.eal,
          currentEal: dash.eal,
          displayEal: dash.eal,
          var95: dash.var95,
          trend: dash.trend,
          telemetry: tel,
          compliance: cmp,
        }
      })
    } catch {
      setState((s) => ({
        ...s,
        panel: 'error',
        errorMessage: 'Risk exposure could not be loaded.',
      }))
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const displayRef = useRef(state.displayEal)
  displayRef.current = state.displayEal

  useEffect(() => {
    const from = displayRef.current
    const to = state.currentEal
    if (from === to) return
    const start = performance.now()
    const duration = 900
    let frame = 0
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration)
      const eased = 1 - (1 - t) ** 3
      const value = Math.round(from + (to - from) * eased)
      setState((s) => ({ ...s, displayEal: value }))
      if (t < 1) frame = requestAnimationFrame(tick)
    }
    frame = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(frame)
  }, [state.currentEal])

  const setBudget = useCallback((n: number) => {
    setState((s) => ({ ...s, budget: n }))
  }, [])

  const applyBudgetPlan = useCallback(() => {
    setState((s) => {
      const plan = optimizeBudget(s.budget, CONTROLS, s.baselineEal, s.approvedControlIds)
      const newly = plan.selectedIds.filter((id) => !s.approvedControlIds.includes(id))
      if (newly.length === 0) return s
      const eal = calculateEAL(plan.selectedIds, CONTROLS, s.baselineEal)
      const names = newly
        .map((id) => CONTROLS.find((c) => c.id === id)?.name)
        .filter(Boolean)
        .join(', ')
      const event: TelemetryEvent = {
        id: `tel-${Date.now()}`,
        timestamp: new Date().toISOString(),
        event: `Budget plan applied: ${names}`,
        source: 'Budget Optimizer',
        severity: 'medium',
        ealImpact: eal - s.currentEal,
        status: 'approved',
      }
      return {
        ...s,
        selectedControlIds: plan.selectedIds,
        approvedControlIds: plan.selectedIds,
        currentEal: eal,
        var95: calculateVaR(eal, s.baselineEal),
        lastApproval: newly[0] ?? s.lastApproval,
        twinPulse: s.twinPulse + 1,
        telemetry: [...s.telemetry, event],
        trend: s.trend.map((p, i) => (i === s.trend.length - 1 ? { ...p, eal } : p)),
        compliance: newly.reduce((rows, id) => {
          const c = CONTROLS.find((x) => x.id === id)
          return c ? applyControlToCompliance(rows, c) : rows
        }, s.compliance),
      }
    })
  }, [])

  const selectNode = useCallback((id: string | null) => {
    setState((s) => {
      if (!id) return { ...s, selectedNodeId: null }
      const shortest = shortestPathToCrownJewel(id)
      return {
        ...s,
        selectedNodeId: id,
        activePathNodeIds: shortest.nodes,
        activePathEdgeIds: shortest.edges,
      }
    })
  }, [])

  const highlightPath = useCallback((pathId: string) => {
    const path = ATTACK_PATHS.find((p) => p.id === pathId)
    if (!path) return
    setState((s) => ({
      ...s,
      activePathNodeIds: path.nodeIds,
      activePathEdgeIds: path.edgeIds,
      selectedNodeId: path.nodeIds[path.nodeIds.length - 2] ?? path.nodeIds[0],
    }))
  }, [])

  const approveControl = useCallback((controlId: string) => {
    setState((s) => {
      if (s.approvedControlIds.includes(controlId)) return s
      const sim = simulateControlChange(s.approvedControlIds, controlId, CONTROLS, s.baselineEal)
      const nextIds = [...s.approvedControlIds, controlId]
      const control = CONTROLS.find((c) => c.id === controlId)
      const event: TelemetryEvent = {
        id: `tel-${Date.now()}`,
        timestamp: new Date().toISOString(),
        event: control ? `${control.name} approved and propagated to twin` : 'Control approved',
        source: 'Control Change',
        severity: 'medium',
        ealImpact: -sim.reduction,
        status: 'approved',
      }
      return {
        ...s,
        selectedControlIds: nextIds,
        approvedControlIds: nextIds,
        currentEal: sim.after,
        var95: calculateVaR(sim.after, s.baselineEal),
        lastApproval: controlId,
        twinPulse: s.twinPulse + 1,
        telemetry: [...s.telemetry, event],
        trend: s.trend.map((p, i) => (i === s.trend.length - 1 ? { ...p, eal: sim.after } : p)),
        compliance: control ? applyControlToCompliance(s.compliance, control) : s.compliance,
      }
    })
  }, [])

  const posture = postureFromEal(state.currentEal, state.baselineEal)

  const value = useMemo<CyrisContextValue>(
    () => ({
      ...state,
      controls: CONTROLS,
      posture,
      contributors: CONTRIBUTORS,
      setBudget,
      applyBudgetPlan,
      selectNode,
      highlightPath,
      approveControl,
      retryLoad: load,
    }),
    [state, posture, setBudget, applyBudgetPlan, selectNode, highlightPath, approveControl, load],
  )

  return <CyrisContext.Provider value={value}>{children}</CyrisContext.Provider>
}

export function useCyris() {
  const ctx = useContext(CyrisContext)
  if (!ctx) throw new Error('useCyris must be used inside CyrisProvider')
  return ctx
}
