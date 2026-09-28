import { useState, useRef, useEffect } from 'react'
import { terminology, type TermDefinition } from '../../utils/terminology'

interface TechnicalTooltipProps {
  termKey: keyof typeof terminology
  customLabel?: string
}

export function TechnicalTooltip({ termKey, customLabel }: TechnicalTooltipProps) {
  const [isOpen, setIsOpen] = useState(false)
  const term: TermDefinition | undefined = terminology[termKey]
  const popoverRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen])

  if (!term) return null

  return (
    <span style={{ position: 'relative', display: 'inline-flex', alignItems: 'center', gap: '4px' }} ref={popoverRef}>
      {customLabel && <span>{customLabel}</span>}
      <button
        type="button"
        className="tooltip-trigger"
        onClick={(e) => {
          e.stopPropagation()
          setIsOpen(!isOpen)
        }}
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
        aria-label={`Explanation for ${term.title}`}
        style={{
          background: 'none',
          border: 'none',
          color: 'var(--accent-blue)',
          cursor: 'pointer',
          padding: '2px 4px',
          fontSize: '0.85rem',
          lineHeight: 1,
          display: 'inline-flex',
          alignItems: 'center',
          opacity: 0.85,
          transition: 'opacity 0.2s ease',
        }}
      >
        ⓘ
      </button>

      {isOpen && (
        <div
          role="tooltip"
          className="tooltip-popover"
          style={{
            position: 'absolute',
            bottom: '125%',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '280px',
            padding: '12px 14px',
            background: 'rgba(15, 23, 42, 0.96)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(59, 130, 246, 0.4)',
            borderRadius: '8px',
            boxShadow: '0 10px 30px rgba(0,0,0,0.6)',
            zIndex: 9999,
            fontSize: '0.82rem',
            lineHeight: 1.5,
            color: '#e2e8f0',
            textAlign: 'left',
            animation: 'fadeIn 0.2s ease-out'
          }}
        >
          <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: '4px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>{term.plainTitle}</span>
            <span style={{ fontSize: '0.7rem', color: '#94a3b8', background: 'rgba(255,255,255,0.06)', padding: '1px 6px', borderRadius: '4px', fontFamily: 'IBM Plex Mono, monospace' }}>
              {term.short}
            </span>
          </div>

          <p style={{ margin: '0 0 8px 0', color: '#cbd5e1' }}>{term.explanation}</p>

          {term.technicalDetails && (
            <div style={{ paddingTop: '6px', borderTop: '1px solid rgba(255,255,255,0.1)', fontSize: '0.75rem', color: '#94a3b8' }}>
              <strong style={{ color: '#cbd5e1' }}>Technical Methodology:</strong> {term.technicalDetails}
            </div>
          )}
        </div>
      )}
    </span>
  )
}

interface ExpandableTechnicalDetailsProps {
  termKey: keyof typeof terminology
  children?: React.ReactNode
}

export function ExpandableTechnicalDetails({ termKey, children }: ExpandableTechnicalDetailsProps) {
  const [expanded, setExpanded] = useState(false)
  const term = terminology[termKey]

  if (!term) return null

  return (
    <div style={{ marginTop: '8px' }}>
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        style={{
          background: 'none',
          border: 'none',
          color: 'var(--accent-blue)',
          cursor: 'pointer',
          padding: '4px 0',
          fontSize: '0.8rem',
          display: 'inline-flex',
          alignItems: 'center',
          gap: '6px',
          fontWeight: 500
        }}
      >
        <span>{expanded ? '▼ Hide Technical Details' : '► ⓘ What does this mean? (Technical View)'}</span>
      </button>

      {expanded && (
        <div
          style={{
            marginTop: '8px',
            padding: '12px 16px',
            background: 'rgba(15, 23, 42, 0.8)',
            borderLeft: '3px solid var(--accent-blue)',
            borderRadius: '0 8px 8px 0',
            fontSize: '0.85rem',
            lineHeight: 1.5,
            color: '#cbd5e1'
          }}
        >
          <div style={{ fontWeight: 600, color: '#ffffff', marginBottom: '4px' }}>
            {term.title} ({term.short})
          </div>
          <p style={{ margin: '0 0 8px 0' }}>{term.explanation}</p>

          {term.technicalDetails && (
            <div style={{ marginTop: '6px', color: '#94a3b8' }}>
              <strong style={{ color: '#e2e8f0' }}>Methodology:</strong> {term.technicalDetails}
            </div>
          )}

          {term.inputs && term.inputs.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <strong style={{ color: '#e2e8f0', fontSize: '0.78rem', textTransform: 'uppercase' }}>Model Inputs:</strong>
              <ul style={{ margin: '4px 0 0 16px', padding: 0, color: '#94a3b8', fontSize: '0.8rem' }}>
                {term.inputs.map((inp) => (
                  <li key={inp}>{inp}</li>
                ))}
              </ul>
            </div>
          )}

          {children}
        </div>
      )}
    </div>
  )
}
