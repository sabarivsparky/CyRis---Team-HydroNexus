import { ComplianceTable } from '../components/Compliance/ComplianceTable'
import { TechnicalTooltip, ExpandableTechnicalDetails } from '../components/common/TechnicalDetails'

export function CompliancePage() {
  return (
    <>
      <div>
        <div className="kicker" style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>REGULATORY STANDARDS AUDIT TRAIL</span>
          <TechnicalTooltip termKey="compliance" />
        </div>
        <h1 style={{ margin: '4px 0 4px', fontSize: '1.5rem', color: '#ffffff' }}>
          REGULATORY AUDIT LEDGER & COMPLIANCE MATRIX
        </h1>
        <p className="muted" style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
          Automatically maps security findings to global and Indian regulatory frameworks including ISO 27001, NIST CSF, RBI CSF (Banking), and SEBI CSCRF (Capital Markets).
        </p>
      </div>

      <ComplianceTable />

      <ExpandableTechnicalDetails termKey="compliance" />
    </>
  )
}
