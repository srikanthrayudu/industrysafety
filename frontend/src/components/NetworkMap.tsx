// React import not required with new JSX transform

type Node = { id: string; label: string; status: string }
type Link = { source: string; target: string; active: boolean }

const positions: Record<string, { x: number; y: number }> = {
  A: { x: 80, y: 80 },
  B: { x: 240, y: 80 },
  C: { x: 240, y: 220 },
  D: { x: 80, y: 220 },
}

type RoutesType = Record<string, { primary?: string[]; current?: string[]; rerouted?: boolean }>

export default function NetworkMap({ nodes, links, routes }: { nodes: Node[]; links: Link[]; routes?: RoutesType }) {
  // build a set of link keys that are in primary and current paths
  const primaryLinks = new Set<string>()
  const currentLinks = new Set<string>()
  if (routes) {
    for (const key of Object.keys(routes)) {
      const r = routes[key]
      const p = r.primary || []
      const c = r.current || []
      for (let i = 0; i < p.length - 1; i++) primaryLinks.add(`${p[i]}-${p[i + 1]}`)
      for (let i = 0; i < c.length - 1; i++) currentLinks.add(`${c[i]}-${c[i + 1]}`)
      for (let i = 0; i < p.length - 1; i++) primaryLinks.add(`${p[i + 1]}-${p[i]}`)
      for (let i = 0; i < c.length - 1; i++) currentLinks.add(`${c[i + 1]}-${c[i]}`)
    }
  }

  return (
    <svg width={360} height={320} className="network-map" style={{ border: '1px solid #e5e7eb', borderRadius: 8 }}>
      {/* links */}
      {links.map((l, i) => {
        const s = positions[l.source]
        const t = positions[l.target]
        const key = `${l.source}-${l.target}`
        const keyRev = `${l.target}-${l.source}`
        let stroke = l.active ? '#111827' : '#9CA3AF'
        let width = 3
        // highlight if link is in current path
        if (currentLinks.has(key) || currentLinks.has(keyRev)) {
          // if it's also in primary -> thick green; else -> orange for backup
          if (primaryLinks.has(key) || primaryLinks.has(keyRev)) {
            stroke = '#059669' // primary active color
            width = 5
          } else {
            stroke = '#f59e0b' // backup used
            width = 5
          }
        }
        return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke={stroke} strokeWidth={width} strokeLinecap="round" />
      })}

      {/* nodes */}
      {nodes.map((n) => {
        const p = positions[n.id] || { x: 10, y: 10 }
        const fill = n.status === 'active' ? '#10B981' : '#EF4444'
        return (
          <g key={n.id}>
            <circle cx={p.x} cy={p.y} r={24} fill={fill} stroke="#111827" strokeWidth={2}></circle>
            <text x={p.x} y={p.y + 40} fontSize={12} textAnchor="middle" fill="#374151">
              {n.label}
            </text>
            <text x={p.x} y={p.y + 56} fontSize={11} textAnchor="middle" fill="#6B7280">
              ({n.id})
            </text>
          </g>
        )
      })}
    </svg>
  )
}

