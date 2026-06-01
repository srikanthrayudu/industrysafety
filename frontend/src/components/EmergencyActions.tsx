import type { EmergencyAction, EmergencyState, RiskLevel } from '../types/simulator'

type EmergencyActionsProps = {
  emergency?: EmergencyState
}

const priorityStyles: Record<RiskLevel, string> = {
  GREEN: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100',
  YELLOW: 'border-yellow-400/30 bg-yellow-400/10 text-yellow-100',
  ORANGE: 'border-orange-500/30 bg-orange-500/10 text-orange-100',
  RED: 'border-red-500/30 bg-red-500/10 text-red-100',
  BLACK: 'border-slate-200/30 bg-black text-slate-100',
}

const statusStyles: Record<string, string> = {
  ready: 'bg-emerald-500/15 text-emerald-200',
  completed: 'bg-emerald-500/15 text-emerald-200',
  queued: 'bg-yellow-400/15 text-yellow-100',
  armed: 'bg-cyan-500/15 text-cyan-100',
  in_progress: 'bg-orange-500/15 text-orange-100',
  delayed: 'bg-orange-500/15 text-orange-100',
  suppressed: 'bg-red-500/15 text-red-100',
  failed: 'bg-red-500/15 text-red-100',
  standby: 'bg-slate-600 text-slate-100',
}

function statusClass(status: string) {
  return statusStyles[status] ?? 'bg-slate-700 text-slate-100'
}

function statusText(status: string) {
  return status.replace(/_/g, ' ')
}

export default function EmergencyActions({ emergency }: EmergencyActionsProps) {
  const actions: EmergencyAction[] = emergency?.actions ?? []

  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100">Emergency Response Actions</h3>
          <p className="mt-1 text-xs text-slate-400">{emergency?.responseMode ?? 'Automatic SIS response'}</p>
        </div>
        <span className="rounded border border-slate-700 bg-slate-950 px-2.5 py-1 text-xs text-slate-300">
          Shutdown {emergency?.shutdownActive ? 'active' : emergency?.lastShutdownStatus ?? 'standby'}
        </span>
      </div>

      <div className="mt-3 max-h-[420px] space-y-2 overflow-y-auto pr-1">
        {actions.map((action) => (
          <div key={action.id} className={`rounded-md border p-3 ${priorityStyles[action.priority]}`}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold">{action.name}</p>
                <p className="mt-1 text-xs opacity-80">{action.target}</p>
              </div>
              <span className={`rounded px-2 py-1 text-[11px] font-semibold ${statusClass(action.status)}`}>
                {statusText(action.status)}
              </span>
            </div>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs opacity-90">
              <span>Owner: {action.owner}</span>
              <span>ETA: {action.etaSeconds.toFixed(2)} s</span>
            </div>
            <p className="mt-2 text-xs opacity-80">{action.reason}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
