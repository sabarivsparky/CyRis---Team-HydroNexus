import { describe, expect, it } from 'vitest'
import { formatINR, formatINRDelta, formatROSI } from './formatINR'
import { BASELINE_EAL, calculateROSI, simulateControlChange } from './riskEngine'
import { CONTROLS } from '../data/mock/controls'

describe('formatINR', () => {
  it('uses Indian grouping', () => {
    expect(formatINR(42_30_000)).toBe('₹42,30,000')
    expect(formatINR(4_20_00_000)).toBe('₹4,20,00,000')
    expect(formatINR(1_25_50_000)).toBe('₹1,25,50,000')
  })

  it('formats deltas', () => {
    expect(formatINRDelta(-18_50_000)).toBe('-₹18,50,000')
    expect(formatINRDelta(7_20_000)).toBe('+₹7,20,000')
  })
})

describe('risk engine', () => {
  it('MFA counterfactual is internally consistent', () => {
    const sim = simulateControlChange([], 'ctrl-mfa', CONTROLS, BASELINE_EAL)
    expect(sim.before).toBe(4_20_00_000)
    expect(sim.cost).toBe(18_00_000)
    expect(sim.after).toBe(3_35_00_000)
    expect(sim.reduction).toBe(85_00_000)
    expect(calculateROSI(sim.reduction, sim.cost).toFixed(2)).toBe('4.72')
    expect(formatROSI(sim.rosi)).toBe('4.72x')
  })
})
