import type { NetworkLink, NetworkNode, RouteInfo } from '../types/simulator'

const positions: Record<string, { x: number; y: number }> = {
  A: { x: 80, y: 120 },
  B: { x: 220, y: 70 },
  C: { x: 360, y: 120 },
  D: { x: 220, y: 210 },
  E: { x: 500, y: 120 },
}

type NetworkMapProps = {
  nodes: NetworkNode[]
  links: NetworkLink[]
  routes: RouteInfo
}

const toLinkKey = (source: string, target: string) => `${source}-${target}`

const shortRoles: Record<string, string> = {
  A: 'Sensors',
  B: 'PLC',
  C: 'SIS',
  D: 'Backup',
  E: 'SCADA',
}

export default function NetworkMap({ nodes, links, routes }: NetworkMapProps) {
  const routeKeys = new Set<string>()
  for (let index = 0; index < routes.current.length - 1; index += 1) {
    const start = routes.current[index]
    const end = routes.current[index + 1]
    routeKeys.add(toLinkKey(start, end))
    routeKeys.add(toLinkKey(end, start))
  }

  const primaryKeys = new Set<string>()
  for (let index = 0; index < routes.primary.length - 1; index += 1) {
    const start = routes.primary[index]
    const end = routes.primary[index + 1]
    primaryKeys.add(toLinkKey(start, end))
    primaryKeys.add(toLinkKey(end, start))
  }

  return (
    <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-3 text-sm text-slate-300">
        <span>Industrial Plant Control Network</span>
        <span className="text-xs text-slate-500">
          Sensor to SCADA: {routes.monitoredFlow.from} to {routes.monitoredFlow.to}
        </span>
      </div>
      <svg width="100%" viewBox="0 0 580 300" className="h-[280px] w-full">
        {links.map((link) => {
          const source = positions[link.source]
          const target = positions[link.target]
          const key = toLinkKey(link.source, link.target)
          const isCurrent = routeKeys.has(key)
          const isPrimary = primaryKeys.has(key)
          let stroke = link.active ? '#334155' : '#7f1d1d'
          if (isCurrent && isPrimary) stroke = '#10b981'
          if (isCurrent && !isPrimary) stroke = '#f59e0b'
          return (
            <line
              key={key}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke={stroke}
              strokeWidth={isCurrent ? 6 : 4}
              strokeLinecap="round"
            />
          )
        })}

        {nodes.map((node) => {
          const point = positions[node.id]
          const fill = node.status === 'active' ? '#059669' : '#dc2626'
          return (
            <g key={node.id}>
              <circle cx={point.x} cy={point.y} r={26} fill={fill} stroke="#0f172a" strokeWidth={3} />
              <text x={point.x} y={point.y + 5} textAnchor="middle" fill="#e2e8f0" fontSize={14} fontWeight={700}>
                {node.id}
              </text>
              <text x={point.x} y={point.y + 42} textAnchor="middle" fill="#94a3b8" fontSize={12}>
                {shortRoles[node.id] ?? node.role}
              </text>
            </g>
          )
        })}
      </svg>

      <div className="mt-2 flex flex-wrap items-center gap-4 text-xs text-slate-300">
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-5 rounded bg-emerald-500" />
          Primary Path
        </span>
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-5 rounded bg-amber-500" />
          Backup Path
        </span>
        <span className="flex items-center gap-2">
          <span className="h-2.5 w-5 rounded bg-red-700" />
          Failed Link
        </span>
      </div>
    </div>
  )
}
