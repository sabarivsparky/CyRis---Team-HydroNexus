import type { ReactNode } from 'react'
import type { PanelState } from '../../types'

export function PanelStatus({
  state,
  loading,
  empty,
  error,
  children,
}: {
  state: PanelState
  loading: string
  empty: string
  error: string
  children: ReactNode
}) {
  if (state === 'loading')
    return (
      <div className="loading-state">
        <div className="spinner" aria-label="Loading" />
        <span>{loading}</span>
      </div>
    )
  if (state === 'error')
    return (
      <div className="error-state">
        <div className="error-icon" aria-hidden="true">!</div>
        <span>{error}</span>
      </div>
    )
  if (state === 'empty') return <div className="panel-state">{empty}</div>
  return children
}
