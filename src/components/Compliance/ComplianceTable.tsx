import { useMemo, useState } from 'react'
import { useCyris } from '../../state/CyrisContext'
import type { Framework, ProofStatus } from '../../types'

const FRAMEWORKS: Array<Framework | 'All'> = ['All', 'ISO 27001', 'NIST CSF', 'RBI CSF', 'SEBI CSCRF']

export function ProofStatusBadge({ status }: { status: ProofStatus }) {
  const isVerified = status === 'verified'
  return (
    <span
      className={`proof ${status}`}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '3px 10px',
        borderRadius: '12px',
        fontSize: '0.75rem',
        fontWeight: 600,
        background: isVerified ? 'rgba(16, 185, 129, 0.15)' : 'rgba(234, 179, 8, 0.15)',
        color: isVerified ? '#10b981' : '#f59e0b',
        border: `1px solid ${isVerified ? 'rgba(16, 185, 129, 0.3)' : 'rgba(234, 179, 8, 0.3)'}`,
        textTransform: 'capitalize'
      }}
    >
      <span
        style={{
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: isVerified ? '#10b981' : '#f59e0b'
        }}
      />
      {status}
    </span>
  )
}

export function FrameworkFilter({
  value,
  onChange,
}: {
  value: Framework | 'All'
  onChange: (v: Framework | 'All') => void
}) {
  return (
    <div className="row filter-row" role="toolbar" aria-label="Framework filter" style={{ gap: '8px', flexWrap: 'wrap' }}>
      {FRAMEWORKS.map((f) => {
        const active = value === f
        return (
          <button
            key={f}
            type="button"
            className="btn"
            aria-pressed={active}
            onClick={() => onChange(f)}
            style={{
              padding: '6px 14px',
              fontSize: '0.85rem',
              background: active ? 'var(--accent-blue-alpha)' : 'rgba(255, 255, 255, 0.03)',
              borderColor: active ? 'var(--accent-blue)' : 'var(--border)',
              color: active ? '#ffffff' : 'var(--text-muted)',
              fontWeight: active ? 600 : 400
            }}
          >
            {f}
          </button>
        )
      })}
    </div>
  )
}

export function ComplianceTable() {
  const { compliance } = useCyris()
  const [fw, setFw] = useState<Framework | 'All'>('All')
  const [search, setSearch] = useState('')

  const rows = useMemo(() => {
    return compliance.filter((r) => {
      const matchFw = fw === 'All' ? true : r.framework === fw
      const matchSearch =
        search.trim() === '' ||
        r.finding.toLowerCase().includes(search.toLowerCase()) ||
        r.control.toLowerCase().includes(search.toLowerCase()) ||
        r.clause.toLowerCase().includes(search.toLowerCase())
      return matchFw && matchSearch
    })
  }, [compliance, fw, search])

  const stats = useMemo(() => {
    const total = compliance.length
    const verified = compliance.filter((c) => c.proof === 'verified').length
    const percent = Math.round((verified / (total || 1)) * 100)
    return { total, verified, percent }
  }, [compliance])

  return (
    <section className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <div className="kicker">REGULATORY AUDIT TRAIL</div>
          <h2>Compliance & Mapping Ledger</h2>
        </div>

        {/* Compliance Progress Badge */}
        <div style={{ padding: '8px 16px', background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '8px', textAlign: 'right' }}>
          <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase' }}>Verified Evidence Ratio</div>
          <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981' }}>
            {stats.verified} / {stats.total} ({stats.percent}%)
          </div>
        </div>
      </div>

      <div style={{ margin: '16px 0 20px 0', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <FrameworkFilter value={fw} onChange={setFw} />

        <input
          type="text"
          placeholder="Filter findings by clause, control, or keyword..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{
            padding: '8px 14px',
            background: 'rgba(0, 0, 0, 0.2)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            color: '#ffffff',
            fontSize: '0.85rem',
            width: '100%',
            maxWidth: '400px'
          }}
        />
      </div>

      {rows.length === 0 ? (
        <p className="panel-state">No mapped findings for this framework or search term.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                <th style={{ padding: '10px' }}>Finding</th>
                <th style={{ padding: '10px' }}>Control</th>
                <th style={{ padding: '10px' }}>Framework</th>
                <th style={{ padding: '10px' }}>Clause</th>
                <th style={{ padding: '10px' }}>Status</th>
                <th style={{ padding: '10px' }}>Evidence</th>
                <th style={{ padding: '10px' }}>Proof Verification</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <td style={{ padding: '10px', fontWeight: 500, color: '#e2e8f0' }}>{r.finding}</td>
                  <td style={{ padding: '10px', color: '#38bdf8' }}>{r.control}</td>
                  <td style={{ padding: '10px' }}>
                    <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.05)', padding: '2px 6px', borderRadius: '4px', fontSize: '0.75rem' }}>
                      {r.framework}
                    </span>
                  </td>
                  <td style={{ padding: '10px', fontFamily: 'IBM Plex Mono, monospace', fontSize: '0.8rem', color: '#cbd5e1' }}>{r.clause}</td>
                  <td style={{ padding: '10px', textTransform: 'capitalize' }}>{r.status}</td>
                  <td style={{ padding: '10px', color: '#94a3b8', fontSize: '0.82rem' }}>{r.evidence}</td>
                  <td style={{ padding: '10px' }}>
                    <ProofStatusBadge status={r.proof} />
                    <div className="num" style={{ fontSize: '0.7rem', marginTop: '4px', opacity: 0.7, fontFamily: 'IBM Plex Mono, monospace' }}>
                      Ref: {r.proofRef}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
