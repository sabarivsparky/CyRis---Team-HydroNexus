import { useState } from 'react'
import { formatINR } from '../../utils/formatINR'
import type { TrendPoint } from '../../types'

export function RiskTrendChart({ points }: { points: TrendPoint[] }) {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null)

  const w = 560
  const h = 200
  const padLeft = 45
  const padRight = 30
  const padTop = 25
  const padBottom = 35

  if (points.length === 0) {
    return <p className="panel-state">No EAL trend points available.</p>
  }

  const maxVal = Math.max(...points.map((p) => p.eal), 1) * 1.15
  const minVal = 0

  const xs = points.map((_, i) => padLeft + (i * (w - padLeft - padRight)) / Math.max(points.length - 1, 1))
  const ys = points.map((p) => h - padBottom - ((p.eal - minVal) / (maxVal - minVal)) * (h - padTop - padBottom))

  // Generate smooth area path
  const linePath = xs.map((x, i) => `${i === 0 ? 'M' : 'L'} ${x} ${ys[i]}`).join(' ')
  const areaPath = `${linePath} L ${xs[xs.length - 1]} ${h - padBottom} L ${xs[0]} ${h - padBottom} Z`

  // Horizontal grid ticks (3 levels)
  const gridTicks = [0, 0.5, 1].map((ratio) => {
    const val = minVal + ratio * (maxVal - minVal)
    const y = h - padBottom - ratio * (h - padTop - padBottom)
    return { val, y }
  })

  const activePoint = hoveredIdx !== null ? points[hoveredIdx] : points[points.length - 1]
  const activeX = hoveredIdx !== null ? xs[hoveredIdx] : xs[xs.length - 1]
  const activeY = hoveredIdx !== null ? ys[hoveredIdx] : ys[ys.length - 1]

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <svg viewBox={`0 0 ${w} ${h}`} role="img" aria-label="EAL trend over six months" width="100%">
        <defs>
          <linearGradient id="ealGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#c9a227" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#c9a227" stopOpacity="0.0" />
          </linearGradient>
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {/* Grid lines */}
        {gridTicks.map((t, idx) => (
          <g key={idx}>
            <line
              x1={padLeft}
              y1={t.y}
              x2={w - padRight}
              y2={t.y}
              stroke="var(--border-subtle)"
              strokeDasharray="4 4"
              strokeWidth="1"
            />
            <text x={padLeft - 8} y={t.y + 4} textAnchor="end" fill="var(--text-muted)" fontSize="9" fontFamily="IBM Plex Mono">
              {formatINR(t.val)}
            </text>
          </g>
        ))}

        {/* Gradient Fill under path */}
        <path d={areaPath} fill="url(#ealGradient)" />

        {/* Trend Line */}
        <path d={linePath} fill="none" stroke="#c9a227" strokeWidth="2.5" filter="url(#glow)" />

        {/* Interactive Dots and Labels */}
        {xs.map((x, i) => (
          <g
            key={points[i].label}
            onMouseEnter={() => setHoveredIdx(i)}
            onMouseLeave={() => setHoveredIdx(null)}
            style={{ cursor: 'pointer' }}
          >
            {/* Extended click target */}
            <rect x={x - 15} y={padTop} width="30" height={h - padTop - padBottom} fill="transparent" />
            <circle
              cx={x}
              cy={ys[i]}
              r={hoveredIdx === i ? 6 : 4}
              fill={hoveredIdx === i ? '#fff' : '#c9a227'}
              stroke="#0a0f18"
              strokeWidth="2"
            />
            <text x={x} y={h - 10} textAnchor="middle" fill={hoveredIdx === i ? '#e8eef7' : '#6d7d91'} fontSize="10" fontWeight={hoveredIdx === i ? '600' : '400'}>
              {points[i].label}
            </text>
          </g>
        ))}

        {/* Active Highlight Line */}
        <line x1={activeX} y1={padTop} x2={activeX} y2={h - padBottom} stroke="#c9a227" strokeDasharray="2 2" opacity="0.6" />

        {/* Active Tooltip / Badge on Chart */}
        <g transform={`translate(${Math.min(activeX, w - 120)}, ${Math.max(activeY - 25, padTop + 10)})`}>
          <rect x="-10" y="-14" width="110" height="22" rx="4" fill="#141e2e" stroke="#c9a227" strokeWidth="1" />
          <text x="45" y="1" textAnchor="middle" fill="#e8eef7" fontSize="10" fontWeight="600" fontFamily="IBM Plex Mono">
            {formatINR(activePoint.eal)}
          </text>
        </g>
      </svg>
    </div>
  )
}
