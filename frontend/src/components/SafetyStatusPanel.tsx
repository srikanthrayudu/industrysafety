import type { Metrics, SafetyStatus, SafetyThresholds } from '../types/simulator'

type SafetyStatusPanelProps = {
  metrics: Metrics
  safety?: SafetyStatus
  thresholds?: SafetyThresholds
}

const levelStyles: Record<NonNullable<SafetyStatus['level']>, string> = {
  normal: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100',
  degraded: 'border-amber-500/40 bg-amber-500/10 text-amber-100',
  critical: 'border-red-500/40 bg-red-500/10 text-red-100',
}

function ThresholdRow({ label, actual, limit, ok }: { label: string; actual: string; limit: string; ok: boolean }) {
  return (
    <div className="grid grid-cols-[1fr_auto_auto] items-center gap-3 border-b border-slate-700 py-2 text-xs last:border-b-0">
      <span className="text-slate-300">{label}</span>
      <span className="font-medium text-slate-100">{actual}</span>
      <span className={ok ? 'text-emerald-300' : 'text-red-300'}>{limit}</span>
    </div>
  )
}

export default function SafetyStatusPanel({ metrics, safety, thresholds }: SafetyStatusPanelProps) {
  const statusLevel = safety?.level ?? 'normal'
  const minReliability = thresholds?.minReliability ?? 99
  const maxDelayMs = thresholds?.maxDelayMs ?? 150
  const maxPacketLossPercent = thresholds?.maxPacketLossPercent ?? 1

  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-100">Safety Threshold Status</h3>
        <span className={`rounded border px-3 py-1 text-xs font-semibold uppercase ${levelStyles[statusLevel]}`}>
          {statusLevel}
        </span>
      </div>

      <div className="mt-3 rounded border border-slate-700 bg-slate-900 px-3">
        <ThresholdRow
          label="Reliability"
          actual={`${metrics.reliability.toFixed(2)}%`}
          limit={`>= ${minReliability}%`}
          ok={metrics.reliability >= minReliability}
        />
        <ThresholdRow
          label="Delay"
          actual={`${metrics.delayMs} ms`}
          limit={`<= ${maxDelayMs} ms`}
          ok={metrics.delayMs <= maxDelayMs}
        />
        <ThresholdRow
          label="Packet Loss"
          actual={`${metrics.packetLossPercent.toFixed(2)}%`}
          limit={`<= ${maxPacketLossPercent}%`}
          ok={metrics.packetLossPercent <= maxPacketLossPercent}
        />
      </div>

      <div className="mt-3 space-y-2">
        {safety?.violations.length ? (
          safety.violations.map((violation) => (
            <div key={violation} className="rounded border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-100">
              {violation}
            </div>
          ))
        ) : (
          <div className="rounded border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-100">
            Communication state is inside configured safety limits.
          </div>
        )}
      </div>
    </section>
  )
}
