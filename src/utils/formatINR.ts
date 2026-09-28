/** Indian grouping: ₹4,20,00,000 — single formatter for all currency. */
export function formatINR(value: number): string {
  const negative = value < 0
  const abs = Math.round(Math.abs(value))
  const raw = String(abs)
  let grouped: string
  if (raw.length <= 3) {
    grouped = raw
  } else {
    const last3 = raw.slice(-3)
    const rest = raw.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ',')
    grouped = `${rest},${last3}`
  }
  return `${negative ? '-' : ''}₹${grouped}`
}

export function formatINRDelta(value: number): string {
  if (value === 0) return formatINR(0)
  const sign = value > 0 ? '+' : ''
  return `${sign}${formatINR(value)}`
}

export function formatROSI(ratio: number): string {
  if (!Number.isFinite(ratio)) return '—'
  return `${ratio.toFixed(2)}x`
}

export function formatPercent(value: number): string {
  return `${Math.round(value * 100)}%`
}

export function formatTimestamp(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleTimeString('en-IN', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}
