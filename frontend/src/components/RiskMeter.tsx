import type { RiskState } from '../types/simulator'

type RiskMeterProps = {
  risk?: RiskState
}

const levelBorder = {
  GREEN: 'border-emerald-500/40',
  YELLOW: 'border-yellow-400/40',
  ORANGE: 'border-orange-500/40',
  RED: 'border-red-500/40',
  BLACK: 'border-slate-300/40',
}

export default function RiskMeter({ risk }: RiskMeterProps) {
  const score = risk?.score ?? 100
  const level = risk?.level ?? 'GREEN'
  const color = risk?.color ?? '#10b981'

  return (
    <section className={`rounded-md border ${levelBorder[level]} bg-slate-800 p-4`}>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100">Risk Meter</h3>
          <p className="mt-1 text-xs text-slate-400">GREEN to BLACK safety state from sensors and communication.</p>
        </div>
        <span className="rounded border border-slate-600 bg-slate-950 px-2.5 py-1 text-xs font-semibold text-slate-100">
          {level}
        </span>
      </div>

      <div className="mt-4 flex flex-col items-center gap-4 sm:flex-row">
        <div
          className="grid h-36 w-36 shrink-0 place-items-center rounded-full"
          style={{ background: `conic-gradient(${color} ${score * 3.6}deg, #334155 0deg)` }}
        >
          <div className="grid h-28 w-28 place-items-center rounded-full bg-slate-900 text-center">
            <div>
              <p className="text-3xl font-semibold text-slate-100">{score.toFixed(0)}</p>
              <p className="text-[11px] uppercase text-slate-500">Safety score</p>
            </div>
          </div>
        </div>

        <div className="min-w-0 flex-1">
          <p className="text-lg font-semibold text-slate-100">{risk?.label ?? 'Normal'}</p>
          <div className="mt-3 space-y-2">
            {risk?.drivers.length ? (
              risk.drivers.map((driver) => (
                <div key={driver} className="rounded border border-slate-700 bg-slate-950/70 px-3 py-2 text-xs text-slate-300">
                  {driver}
                </div>
              ))
            ) : (
              <div className="rounded border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-100">
                No abnormal safety drivers detected.
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
