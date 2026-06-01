import type { NetworkNode } from '../types/simulator'

type NodeCardProps = {
  node: NetworkNode
  onFail: (nodeId: string) => void
  onRestore: (nodeId: string) => void
}

export default function NodeCard({ node, onFail, onRestore }: NodeCardProps) {
  const isHealthy = node.status === 'active'
  return (
    <div className="rounded-md border border-slate-700 bg-slate-800 p-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-slate-100">{node.label}</p>
          <p className="text-xs text-slate-400">{node.role}</p>
        </div>
        <span
          className={`rounded px-2 py-1 text-xs font-semibold ${
            isHealthy ? 'bg-emerald-800 text-emerald-200' : 'bg-red-900 text-red-200'
          }`}
        >
          {node.status.toUpperCase()}
        </span>
      </div>
      <div className="mt-3">
        {isHealthy ? (
          <button
            onClick={() => onFail(node.id)}
            className="w-full rounded bg-red-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-red-500"
          >
            Simulate Failure
          </button>
        ) : (
          <button
            onClick={() => onRestore(node.id)}
            className="w-full rounded bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500"
          >
            Restore Node
          </button>
        )}
      </div>
    </div>
  )
}
