import type { Hazard, RiskLevel } from '../types/simulator'

type HazardDetectionPanelProps = {
  hazards?: Hazard[]
}

const levelStyles: Record<RiskLevel, string> = {
  GREEN: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-100',
  YELLOW: 'border-yellow-400/30 bg-yellow-400/10 text-yellow-100',
  ORANGE: 'border-orange-500/30 bg-orange-500/10 text-orange-100',
  RED: 'border-red-500/30 bg-red-500/10 text-red-100',
  BLACK: 'border-slate-200/30 bg-black text-slate-100',
}

export default function HazardDetectionPanel({ hazards = [] }: HazardDetectionPanelProps) {
  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="flex items-center justify-between gap-3">
        <h3 className="text-sm font-semibold text-slate-100">Hazard Detection</h3>
        <span className="rounded border border-slate-700 bg-slate-950 px-2.5 py-1 text-xs text-slate-300">
          {hazards.length} active
        </span>
      </div>

      <div className="mt-3 max-h-[420px] space-y-3 overflow-y-auto pr-1">
        {hazards.length === 0 ? (
          <div className="rounded border border-emerald-500/30 bg-emerald-500/10 px-3 py-3 text-sm text-emerald-100">
            No abnormal process hazards detected.
          </div>
        ) : null}

        {hazards.map((hazard) => (
          <div key={hazard.id} className={`rounded-md border p-3 ${levelStyles[hazard.level]}`}>
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-sm font-semibold">{hazard.name}</p>
                <p className="mt-1 text-xs opacity-80">{hazard.domain}</p>
              </div>
              <span className="rounded bg-slate-950/60 px-2 py-1 text-[11px] font-bold">{hazard.level}</span>
            </div>
            <p className="mt-2 text-xs leading-5 opacity-90">{hazard.description}</p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
              <span>Reading: {hazard.reading} {hazard.unit}</span>
              <span>Limit: {hazard.threshold}</span>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              {hazard.recommendedActions.slice(0, 3).map((action) => (
                <span key={action} className="rounded border border-current/20 bg-slate-950/40 px-2 py-1 text-[11px]">
                  {action}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
