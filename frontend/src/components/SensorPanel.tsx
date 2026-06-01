import type { RiskLevel, SensorReading } from '../types/simulator'

type SensorPanelProps = {
  sensors?: SensorReading[]
}

const riskStyles: Record<RiskLevel, string> = {
  GREEN: 'bg-emerald-500 text-emerald-950',
  YELLOW: 'bg-yellow-300 text-yellow-950',
  ORANGE: 'bg-orange-400 text-orange-950',
  RED: 'bg-red-500 text-white',
  BLACK: 'bg-black text-white ring-1 ring-slate-400/60',
}

const barStyles: Record<RiskLevel, string> = {
  GREEN: 'bg-emerald-500',
  YELLOW: 'bg-yellow-300',
  ORANGE: 'bg-orange-400',
  RED: 'bg-red-500',
  BLACK: 'bg-slate-100',
}

function percent(sensor: SensorReading) {
  if (sensor.max <= sensor.min) return 0
  return Math.max(4, Math.min(100, ((sensor.value - sensor.min) / (sensor.max - sensor.min)) * 100))
}

export default function SensorPanel({ sensors = [] }: SensorPanelProps) {
  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-100">Safety Sensor Status</h3>
        <span className="text-xs text-slate-400">{sensors.length} simulated sensors</span>
      </div>

      <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        {sensors.map((sensor) => (
          <div key={sensor.id} className="rounded-md border border-slate-700 bg-slate-950/70 p-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-slate-100">{sensor.label}</p>
                <p className="text-xs text-slate-500">{sensor.domain}</p>
              </div>
              <span className={`rounded px-2 py-1 text-[11px] font-bold ${riskStyles[sensor.riskLevel]}`}>
                {sensor.riskLevel}
              </span>
            </div>

            <div className="mt-3 flex items-end justify-between gap-3">
              <div>
                <p className="text-2xl font-semibold text-slate-100">
                  {sensor.value}
                  <span className="ml-1 text-sm text-slate-400">{sensor.unit}</span>
                </p>
                <p className="mt-1 text-xs text-slate-500">{sensor.normalRange}</p>
              </div>
              <span className={sensor.status === 'online' ? 'text-xs text-emerald-300' : 'text-xs text-red-300'}>
                {sensor.status}
              </span>
            </div>

            <div className="mt-3 h-2 overflow-hidden rounded bg-slate-700">
              <div className={`h-full ${barStyles[sensor.riskLevel]}`} style={{ width: `${percent(sensor)}%` }} />
            </div>
            <p className="mt-2 truncate text-xs text-slate-500">Limit: {sensor.threshold}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
