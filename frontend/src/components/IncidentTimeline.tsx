import type { Alert, LogEntry } from '../types/simulator'

type IncidentTimelineProps = {
  logs: LogEntry[]
  alerts: Alert[]
}

export default function IncidentTimeline({ logs, alerts }: IncidentTimelineProps) {
  const alertItems = alerts.slice(-6).map((alert) => ({
    time: alert.time,
    event: alert.message,
    kind: alert.level,
  }))
  const logItems = logs.slice(-8).map((log) => ({
    time: log.time,
    event: log.event,
    kind: 'log',
  }))
  const items = [...alertItems, ...logItems].slice(-10).reverse()

  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <h3 className="text-sm font-semibold text-slate-100">Historical Event Timeline</h3>
      <div className="mt-3 max-h-72 space-y-2 overflow-y-auto pr-1">
        {items.length === 0 ? <p className="text-sm text-slate-400">No incident events recorded.</p> : null}
        {items.map((item, index) => (
          <div key={`${item.time}-${index}`} className="grid grid-cols-[70px_1fr] gap-3 rounded border border-slate-700 bg-slate-950/70 px-3 py-2 text-sm">
            <span className="text-xs text-slate-500">{item.time}</span>
            <span className={item.kind === 'critical' ? 'text-red-200' : item.kind === 'warning' ? 'text-yellow-100' : 'text-slate-300'}>
              {item.event}
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
