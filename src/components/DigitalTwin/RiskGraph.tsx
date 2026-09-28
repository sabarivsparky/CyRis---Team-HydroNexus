import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { GRAPH_EDGES, GRAPH_NODES } from '../../data/mock/attackGraph'
import { useCyris } from '../../state/CyrisContext'
import type { NodeType } from '../../types'

const TYPE_FILL: Record<NodeType, string> = {
  asset: '#4f8fbf',
  identity: '#e08a3c',
  control: '#3d9a7a',
  vulnerability: '#e05a4f',
  'crown-jewel': '#c9a227',
  external: '#6d7d91',
}

export function RiskGraph() {
  const ref = useRef<SVGSVGElement | null>(null)
  const { selectedNodeId, activePathNodeIds, activePathEdgeIds, approvedControlIds, selectNode } = useCyris()

  useEffect(() => {
    const svg = d3.select(ref.current)
    svg.selectAll('*').remove()
    const width = 980
    const height = 520
    svg.attr('viewBox', `0 0 ${width} ${height}`)

    const hardened = new Set<string>()
    if (approvedControlIds.includes('ctrl-mfa')) hardened.add('n-mfa')
    if (approvedControlIds.includes('ctrl-seg')) hardened.add('n-seg')
    if (approvedControlIds.includes('ctrl-cve')) {
      hardened.add('n-vuln')
      hardened.add('n-api')
    }
    if (approvedControlIds.includes('ctrl-edr')) hardened.add('n-auth')

    const isMfaApproved = approvedControlIds.includes('ctrl-mfa')

    const defs = svg.append('defs')

    // Glow filter
    const filter = defs.append('filter').attr('id', 'nodeGlow').attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%')
    filter.append('feGaussianBlur').attr('stdDeviation', '4').attr('result', 'blur')
    filter.append('feComposite').attr('in', 'SourceGraphic').attr('in2', 'blur').attr('operator', 'over')

    // Red glow filter for attack path
    const redGlow = defs.append('filter').attr('id', 'redPathGlow').attr('x', '-50%').attr('y', '-50%').attr('width', '200%').attr('height', '200%')
    redGlow.append('feGaussianBlur').attr('stdDeviation', '5').attr('result', 'blur')
    redGlow.append('feComposite').attr('in', 'SourceGraphic').attr('in2', 'blur').attr('operator', 'over')

    // Arrow markers
    defs.append('marker')
      .attr('id', 'arrow')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 20)
      .attr('refY', 5)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M 0 0 L 10 5 L 0 10 z')
      .attr('fill', '#3a4d68')

    defs.append('marker')
      .attr('id', 'arrow-active')
      .attr('viewBox', '0 0 10 10')
      .attr('refX', 22)
      .attr('refY', 5)
      .attr('markerWidth', 7)
      .attr('markerHeight', 7)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M 0 0 L 10 5 L 0 10 z')
      .attr('fill', isMfaApproved ? '#10b981' : '#e05a4f')

    const g = svg.append('g').attr('class', 'graph-root-group')
    const nodeBy = new Map(GRAPH_NODES.map((n) => [n.id, n]))

    // Render Edges
    const edgesGroup = g.append('g').attr('class', 'edges-group')

    GRAPH_EDGES.forEach((edge) => {
      const source = nodeBy.get(edge.source)
      const target = nodeBy.get(edge.target)
      if (!source || !target) return

      const isActive = activePathEdgeIds.includes(edge.id)
      const strokeColor = isActive ? (isMfaApproved ? '#10b981' : '#e05a4f') : '#1e293b'
      const strokeWidth = isActive ? (isMfaApproved ? 2 : 3.5) : 1.5
      const opacity = activePathEdgeIds.length && !isActive ? 0.25 : 1

      // Draw base edge line
      const line = edgesGroup
        .append('line')
        .attr('x1', source.x)
        .attr('y1', source.y)
        .attr('x2', target.x)
        .attr('y2', target.y)
        .attr('stroke', strokeColor)
        .attr('stroke-width', strokeWidth)
        .attr('opacity', opacity)
        .attr('marker-end', isActive ? 'url(#arrow-active)' : 'url(#arrow)')
        .attr('filter', isActive && !isMfaApproved ? 'url(#redPathGlow)' : 'none')

      if (isActive) {
        line.attr('class', 'attack-edge-animated')
      }

      // Add SVG animated attack particle along active edges
      if (isActive && !isMfaApproved) {
        const pathId = `path-${edge.id}`
        edgesGroup
          .append('path')
          .attr('id', pathId)
          .attr('d', `M ${source.x} ${source.y} L ${target.x} ${target.y}`)
          .attr('fill', 'none')
          .attr('stroke', 'transparent')

        const particle = edgesGroup
          .append('circle')
          .attr('r', 4.5)
          .attr('fill', '#ef4444')
          .attr('filter', 'url(#redPathGlow)')

        const anim = document.createElementNS('http://www.w3.org/2000/svg', 'animateMotion')
        anim.setAttribute('dur', '1.5s')
        anim.setAttribute('repeatCount', 'indefinite')
        const mpath = document.createElementNS('http://www.w3.org/2000/svg', 'mpath')
        mpath.setAttributeNS('http://www.w3.org/1999/xlink', 'href', `#${pathId}`)
        anim.appendChild(mpath)
        particle.node()?.appendChild(anim)
      }
    })

    // Nodes Group
    const nodesGroup = g.append('g').attr('class', 'nodes-group')

    const nodes = nodesGroup
      .selectAll('g.node')
      .data(GRAPH_NODES)
      .enter()
      .append('g')
      .attr('class', (d) => `node ${d.type === 'crown-jewel' ? 'crown-jewel-animated' : ''}`)
      .attr('tabindex', 0)
      .attr('role', 'button')
      .attr('aria-label', (d) => `${d.name}, ${d.type}`)
      .attr('transform', (d) => `translate(${d.x},${d.y})`)
      .style('cursor', 'pointer')
      .on('click', (_, d) => selectNode(d.id))
      .on('keydown', (event, d) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          selectNode(d.id)
        }
      })

    // Protective Pulse for Hardened / Control Nodes
    nodes
      .filter((d) => hardened.has(d.id) || d.type === 'control')
      .append('circle')
      .attr('r', 26)
      .attr('fill', 'none')
      .attr('stroke', '#10b981')
      .attr('stroke-width', 1.5)
      .attr('stroke-dasharray', '4 2')
      .attr('opacity', 0.6)

    // Outer aura ring for selected or active path nodes
    nodes
      .append('circle')
      .attr('r', (d) => (d.type === 'crown-jewel' ? 28 : 22))
      .attr('fill', 'none')
      .attr('stroke', (d) => {
        if (d.id === selectedNodeId) return '#3b82f6'
        if (activePathNodeIds.includes(d.id)) return isMfaApproved ? '#10b981' : '#ef4444'
        if (hardened.has(d.id)) return '#10b981'
        return 'none'
      })
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', (d) => (d.id === selectedNodeId ? '4 2' : 'none'))
      .attr('opacity', 0.85)

    // Node Main Circle
    nodes
      .append('circle')
      .attr('r', (d) => (d.type === 'crown-jewel' ? 22 : 16))
      .attr('fill', (d) => TYPE_FILL[d.type])
      .attr('stroke', (d) => {
        if (d.id === selectedNodeId) return '#ffffff'
        if (hardened.has(d.id)) return '#10b981'
        if (activePathNodeIds.includes(d.id)) return isMfaApproved ? '#10b981' : '#f87171'
        return '#0f172a'
      })
      .attr('stroke-width', (d) => (d.id === selectedNodeId || activePathNodeIds.includes(d.id) ? 3 : 1.5))
      .attr('filter', (d) => (d.id === selectedNodeId || d.type === 'crown-jewel' ? 'url(#nodeGlow)' : 'none'))

    // Hardened Badge indicator
    nodes
      .filter((d) => hardened.has(d.id))
      .append('circle')
      .attr('cx', 12)
      .attr('cy', -12)
      .attr('r', 6)
      .attr('fill', '#10b981')
      .attr('stroke', '#0a0f18')
      .attr('stroke-width', 1.5)

    // Crown Jewel Badge Tag
    nodes
      .filter((d) => d.type === 'crown-jewel')
      .append('text')
      .attr('y', -30)
      .attr('text-anchor', 'middle')
      .attr('fill', '#fde047')
      .attr('font-size', 9)
      .attr('font-weight', 'bold')
      .attr('font-family', 'IBM Plex Mono, monospace')
      .text('👑 CRITICAL ASSET')

    // Node Label
    nodes
      .append('text')
      .attr('y', (d) => (d.type === 'crown-jewel' ? 38 : 32))
      .attr('text-anchor', 'middle')
      .attr('fill', (d) => (d.id === selectedNodeId ? '#ffffff' : '#cbd5e1'))
      .attr('font-size', 11)
      .attr('font-weight', (d) => (d.id === selectedNodeId || d.type === 'crown-jewel' ? '600' : '400'))
      .attr('font-family', 'IBM Plex Sans, sans-serif')
      .text((d) => d.name)

  }, [selectedNodeId, activePathNodeIds, activePathEdgeIds, approvedControlIds, selectNode])

  return <svg ref={ref} className="graph-canvas" role="img" aria-label="Enterprise attack-path digital twin" />
}
