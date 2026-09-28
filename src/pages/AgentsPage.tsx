import { AGENT_RECORDS } from '../data/mock/agents'
import { BlueAgentResponse, JudgeDecision, RedAgentFinding } from '../components/Agents/AgentPanels'
import { TechnicalTooltip, ExpandableTechnicalDetails } from '../components/common/TechnicalDetails'

export function AgentsPage() {
  const record = AGENT_RECORDS[0]
  if (!record) {
    return <p className="panel-state">No agent decision records are available.</p>
  }

  return (
    <>
      <div>
        <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>AI EVIDENCE ARBITRATION</span>
          <TechnicalTooltip termKey="monteCarlo" />
        </div>
        <h1 style={{ margin: '4px 0 4px', fontSize: '1.5rem', color: '#ffffff' }}>
          RISK DECISION AGENTS: {record.title}
        </h1>
        <p className="muted" style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
          An auditable evidence debate between Red Exploit Analyst, Blue Control Defender, and Judge Arbitrator grounded in live system telemetry.
        </p>
      </div>

      <div className="agents">
        <RedAgentFinding record={record} />
        <BlueAgentResponse record={record} />
        <JudgeDecision record={record} />
      </div>

      <ExpandableTechnicalDetails termKey="monteCarlo" />
    </>
  )
}
