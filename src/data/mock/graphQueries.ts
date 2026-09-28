import { ATTACK_PATHS, CROWN_JEWEL_ID, GRAPH_EDGES, GRAPH_NODES } from './attackGraph'
import type { GraphNode } from '../../types'

export function nodeById(id: string): GraphNode | undefined {
  return GRAPH_NODES.find((n) => n.id === id)
}

export function neighbors(id: string): string[] {
  return GRAPH_EDGES.filter((e) => e.source === id || e.target === id).map((e) =>
    e.source === id ? e.target : e.source,
  )
}

/** BFS shortest path to crown jewel. */
export function shortestPathToCrownJewel(fromId: string): { nodes: string[]; edges: string[] } {
  if (fromId === CROWN_JEWEL_ID) return { nodes: [fromId], edges: [] }
  const q: string[][] = [[fromId]]
  const seen = new Set([fromId])
  while (q.length) {
    const path = q.shift()
    if (!path) break
    const last = path[path.length - 1]
    for (const n of neighbors(last)) {
      if (seen.has(n)) continue
      const next = [...path, n]
      if (n === CROWN_JEWEL_ID) {
        const edges: string[] = []
        for (let i = 0; i < next.length - 1; i += 1) {
          const edge = GRAPH_EDGES.find(
            (e) =>
              (e.source === next[i] && e.target === next[i + 1]) ||
              (e.target === next[i] && e.source === next[i + 1]),
          )
          if (edge) edges.push(edge.id)
        }
        return { nodes: next, edges }
      }
      seen.add(n)
      q.push(next)
    }
  }
  return { nodes: [fromId], edges: [] }
}

export function primaryPathForNode(nodeId: string) {
  return ATTACK_PATHS.find((p) => p.nodeIds.includes(nodeId)) ?? ATTACK_PATHS[0]
}
