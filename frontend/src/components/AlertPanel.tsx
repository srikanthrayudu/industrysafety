import type { Alert } from '../types/simulator'

type AlertPanelProps = {
  alerts: Alert[]
}

const levelStyles: Record<Alert['level'], string> = {
  warning: 'border-amber-500/30 bg-amber-500/10 text-amber-200',
  critical: 'border-red-500/30 bg-red-500/10 text-red-200',
  success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200',
}

export default function AlertPanel({ alerts }: AlertPanelProps) {
  return (
    <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <h3 className="text-sm font-semibold text-slate-100">Alerts</h3>
      <div className="mt-3 max-h-52 space-y-2 overflow-y-auto">
        {alerts.length === 0 && <p className="text-sm text-slate-400">No active alerts</p>}
        {alerts
          .slice()
          .reverse()
          .map((alert, index) => (
            <div key={`${alert.time}-${index}`} className={`rounded border px-3 py-2 text-sm ${levelStyles[alert.level]}`}>
              <div className="flex items-start justify-between gap-3">
                <span>{alert.message}</span>
                <span className="text-xs opacity-80">{alert.time}</span>
              </div>
            </div>
          ))}
      </div>
    </div>
  )
}
