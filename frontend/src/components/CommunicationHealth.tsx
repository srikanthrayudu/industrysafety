import type { CommunicationState, Metrics, RouteInfo } from '../types/simulator'

type CommunicationHealthProps = {
  communication?: CommunicationState
  metrics: Metrics
  routes: RouteInfo
}

function HealthRow({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="flex items-center justify-between gap-3 border-b border-slate-700 py-2 text-sm last:border-b-0">
      <span className="text-slate-400">{label}</span>
      <span className={`font-semibold ${tone}`}>{value}</span>
    </div>
  )
}

function pathText(path: string[]) {
  return path.length > 0 ? path.join(' -> ') : 'No active route'
}

export default function CommunicationHealth({ communication, metrics, routes }: CommunicationHealthProps) {
  const reliability = communication?.safetyCommunicationReliability ?? metrics.reliability
  const alarmRate = communication?.alarmDeliverySuccessRate ?? metrics.alarmDeliverySuccessRate ?? 100
  const shutdownRate = communication?.emergencyShutdownSuccessRate ?? metrics.emergencyShutdownSuccessRate ?? 100
  const activePath = communication?.currentPath ?? routes.current

  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100">Safety Communication Health</h3>
          <p className="mt-1 text-xs text-slate-400">Reliability interpreted as alarm and shutdown delivery quality.</p>
        </div>
        <span
          className={`rounded border px-2.5 py-1 text-xs font-semibold ${
            routes.backupActive ? 'border-amber-400/40 bg-amber-400/10 text-amber-100' : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100'
          }`}
        >
          {routes.backupActive ? 'Backup route' : 'Primary route'}
        </span>
      </div>

      <div className="mt-3 rounded-md border border-slate-700 bg-slate-950/70 px-3">
        <HealthRow label="Safety communication reliability" value={`${reliability.toFixed(2)}%`} tone="text-emerald-300" />
        <HealthRow label="Alarm delivery success" value={`${alarmRate.toFixed(2)}%`} tone="text-cyan-300" />
        <HealthRow label="Emergency shutdown success" value={`${shutdownRate.toFixed(2)}%`} tone="text-orange-300" />
        <HealthRow label="Average response delay" value={`${metrics.delayMs} ms`} tone="text-slate-100" />
        <HealthRow label="Missed sensor readings" value={`${communication?.missedSensorReadings ?? metrics.packetsLost}`} tone="text-red-300" />
      </div>

      <div className="mt-3 rounded-md border border-slate-700 bg-slate-950/70 p-3">
        <p className="text-xs uppercase text-slate-500">Active control path</p>
        <p className="mt-1 text-sm font-medium text-slate-100">{pathText(activePath)}</p>
      </div>
    </section>
  )
}
