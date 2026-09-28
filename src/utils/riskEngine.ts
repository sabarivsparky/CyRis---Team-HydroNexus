import type { OptimizationResult, SecurityControl, Severity } from '../types'

export const BASELINE_EAL = 4_20_00_000
export const BASELINE_VAR95 = 18_00_00_000

/** ROSI as risk-reduction / cost (matches demo: ₹85L / ₹18L = 4.72x). */
export function calculateROSI(riskReduction: number, cost: number): number {
  if (cost <= 0) return 0
  return riskReduction / cost
}

export function calculateVaR(eal: number, baselineEal = BASELINE_EAL, baselineVar = BASELINE_VAR95): number {
  const scale = baselineEal === 0 ? 1 : eal / baselineEal
  return Math.round(baselineVar * scale)
}

/**
 * Submodular risk reduction: each added control's marginal value declines
 * as residual exposure shrinks (overlapping blast-radius coverage).
 */
export function calculateRiskReduction(
  selectedIds: string[],
  controls: SecurityControl[],
  baselineEal: number,
): number {
  const selected = selectedIds
    .map((id) => controls.find((c) => c.id === id))
    .filter((c): c is SecurityControl => Boolean(c))

  let remaining = baselineEal
  let total = 0
  for (const control of selected) {
    const coverage = Math.min(1, control.standaloneReduction / baselineEal)
    const marginal = remaining * coverage
    total += marginal
    remaining -= marginal
  }
  return Math.round(total)
}

export function calculateEAL(
  selectedIds: string[],
  controls: SecurityControl[],
  baselineEal: number,
): number {
  const reduction = calculateRiskReduction(selectedIds, controls, baselineEal)
  return Math.max(0, Math.round(baselineEal - reduction))
}

export function simulateControlChange(
  selectedIds: string[],
  nextId: string,
  controls: SecurityControl[],
  baselineEal: number,
): { before: number; after: number; reduction: number; cost: number; rosi: number } {
  const before = calculateEAL(selectedIds, controls, baselineEal)
  const afterIds = selectedIds.includes(nextId) ? selectedIds : [...selectedIds, nextId]
  const after = calculateEAL(afterIds, controls, baselineEal)
  const control = controls.find((c) => c.id === nextId)
  const cost = control?.cost ?? 0
  const reduction = before - after
  return { before, after, reduction, cost, rosi: calculateROSI(reduction, cost) }
}

/** Greedy ROSI pack under a budget ceiling (deterministic). */
export function optimizeBudget(
  budget: number,
  controls: SecurityControl[],
  baselineEal: number,
  alreadySelected: string[] = [],
): OptimizationResult {
  const remainingControls = controls
    .filter((c) => !alreadySelected.includes(c.id))
    .slice()
    .sort((a, b) => calculateROSI(b.standaloneReduction, b.cost) - calculateROSI(a.standaloneReduction, a.cost))

  const selected = [...alreadySelected]
  let spent = controls.filter((c) => alreadySelected.includes(c.id)).reduce((s, c) => s + c.cost, 0)

  for (const control of remainingControls) {
    if (spent + control.cost <= budget) {
      selected.push(control.id)
      spent += control.cost
    }
  }

  const riskReduction = calculateRiskReduction(selected, controls, baselineEal)
  const resultingEal = Math.max(0, baselineEal - riskReduction)
  return {
    selectedIds: selected,
    estimatedCost: spent,
    riskReduction,
    resultingEal,
    rosi: calculateROSI(riskReduction, spent),
    remainingBudget: budget - spent,
  }
}

export function postureFromEal(eal: number, baseline = BASELINE_EAL): Severity {
  const ratio = eal / baseline
  if (ratio >= 0.85) return 'critical'
  if (ratio >= 0.55) return 'high'
  if (ratio >= 0.3) return 'medium'
  return 'low'
}

export function investmentCurve(
  controls: SecurityControl[],
  baselineEal: number,
  steps = 8,
): { spend: number; eal: number; reduction: number }[] {
  const maxSpend = controls.reduce((s, c) => s + c.cost, 0)
  const points: { spend: number; eal: number; reduction: number }[] = []
  for (let i = 0; i <= steps; i += 1) {
    const budget = Math.round((maxSpend * i) / steps)
    const opt = optimizeBudget(budget, controls, baselineEal)
    points.push({ spend: opt.estimatedCost || budget, eal: opt.resultingEal, reduction: opt.riskReduction })
  }
  return points
}
