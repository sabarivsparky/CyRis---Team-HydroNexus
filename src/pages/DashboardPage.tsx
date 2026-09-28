import { PanelStatus } from '../components/common/PanelStatus'
import { BudgetOptimizer, InvestmentCurve, RecentEvents } from '../components/Dashboard/BudgetOptimizer'
import { EALHero } from '../components/Dashboard/EALHero'
import { RiskContributors } from '../components/Dashboard/RiskContributors'
import { RiskTrendChart } from '../components/Dashboard/RiskTrendChart'
import { TechnicalTooltip } from '../components/common/TechnicalDetails'
import { useCyris } from '../state/CyrisContext'

export function DashboardPage() {
  const { panel, errorMessage, displayEal, var95, posture, trend, contributors, retryLoad } = useCyris()

  if (panel === 'error') {
    return (
      <div className="card" style={{ padding: '24px', textAlign: 'center' }}>
        <h3 style={{ color: '#ef4444', marginBottom: '8px' }}>Risk information couldn't be loaded</h3>
        <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '16px' }}>
          {errorMessage || 'Unable to connect to the risk engine calculations.'}
        </p>
        <button type="button" className="btn primary" onClick={retryLoad}>
          Try Again
        </button>
      </div>
    )
  }

  return (
    <>
      <div style={{ background: 'rgba(56, 189, 248, 0.06)', border: '1px solid rgba(56, 189, 248, 0.2)', padding: '10px 16px', borderRadius: '8px', marginBottom: '16px', fontSize: '0.85rem', color: '#38bdf8', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          💡 <strong>Boardroom Decision Flow:</strong> 1. Review Yearly Exposure → 2. Identify Risk Drivers → 3. Simulate Protection Impact → 4. Approve Safeguards.
        </div>
        <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>SIH26105 · BOARD DEMO MODE</div>
      </div>

      <PanelStatus
        state={panel}
        loading="Calculating financial risk exposure across enterprise assets..."
        empty="No risk exposure is currently modelled."
        error={errorMessage || 'Risk information couldn\'t be loaded.'}
      >
        {/* Core Risk & Trend Hero Grid */}
        <div className="grid-3" style={{ marginBottom: '20px' }}>
          <EALHero eal={displayEal} var95={var95} posture={posture} />

          <section className="card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.8))' }}>
            <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span>6-MONTH EXPOSURE TREND</span>
              <TechnicalTooltip termKey="EAL" />
            </div>
            <h3 style={{ fontSize: '1.15rem', color: '#ffffff', margin: '4px 0 12px 0' }}>
              EXPECTED LOSS TRAJECTORY
            </h3>
            <RiskTrendChart points={trend} />
          </section>

          <RecentEvents />
        </div>

        {/* Risk Drivers & Budget Protection Planner */}
        <div className="grid-contributors" style={{ marginBottom: '20px' }}>
          <section className="card">
            <RiskContributors items={contributors} />
          </section>

          <BudgetOptimizer />
        </div>

        {/* ROSI Investment Curve */}
        <InvestmentCurve />
      </PanelStatus>
    </>
  )
}
