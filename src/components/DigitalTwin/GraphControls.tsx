import { ATTACK_PATHS } from '../../data/mock/attackGraph'
import { useCyris } from '../../state/CyrisContext'

export function GraphControls() {
  const { highlightPath, selectNode, activePathNodeIds } = useCyris()
  return (
    <div className="row filter-row" style={{ marginBottom: 8 }} role="toolbar" aria-label="Attack path selection">
      {ATTACK_PATHS.map((p) => (
        <button
          key={p.id}
          type="button"
          className="btn"
          aria-pressed={p.nodeIds.every((id) => activePathNodeIds.includes(id))}
          onClick={() => highlightPath(p.id)}
        >
          {p.name}
        </button>
      ))}
      <button type="button" className="btn" onClick={() => selectNode(null)}>
        Clear selection
      </button>
    </div>
  )
}
