import type { PlantProfile, RiskState, SafetyMetrics, ScenarioState } from '../types/simulator'

type PlantOverviewProps = {
  plant?: PlantProfile
  risk?: RiskState
  safetyMetrics?: SafetyMetrics
  scenario?: ScenarioState
}

const riskStyles = {
  GREEN: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-100',
  YELLOW: 'border-yellow-400/40 bg-yellow-400/10 text-yellow-100',
  ORANGE: 'border-orange-500/40 bg-orange-500/10 text-orange-100',
  RED: 'border-red-500/40 bg-red-500/10 text-red-100',
  BLACK: 'border-slate-200/30 bg-black text-slate-100',
}

function ScoreTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-md border border-slate-700 bg-slate-950/70 px-3 py-2">
      <p className="text-[11px] uppercase text-slate-500">{label}</p>
      <p className="mt-1 text-lg font-semibold text-slate-100">{value}</p>
    </div>
  )
}

export default function PlantOverview({ plant, risk, safetyMetrics, scenario }: PlantOverviewProps) {
  const riskLevel = risk?.level ?? 'GREEN'
  const activeScenario = scenario?.activeScenarioLabel ?? plant?.activeScenario ?? 'Normal Operation'

  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="max-w-3xl">
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded border px-2.5 py-1 text-xs font-semibold ${riskStyles[riskLevel]}`}>
              {riskLevel} / {risk?.label ?? 'Normal'}
            </span>
            <span className="rounded border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1 text-xs font-semibold text-cyan-100">
              {plant?.mode ?? 'Normal Operation'}
            </span>
          </div>
          <h2 className="mt-3 text-xl font-semibold text-slate-100">
            {plant?.name ?? 'Integrated Hazardous Process Facility'}
          </h2>
          <p className="mt-1 text-sm text-slate-300">{plant?.processArea ?? 'Multi-domain training simulator'}</p>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-400">
            {plant?.description ??
              'Chemical, nuclear, mining, oil and gas, and hazardous manufacturing safety training.'}
          </p>
        </div>

        <div className="min-w-[220px] rounded-md border border-slate-700 bg-slate-950/70 px-3 py-3">
          <p className="text-[11px] uppercase text-slate-500">Active scenario</p>
          <p className="mt-1 text-sm font-semibold text-slate-100">{activeScenario}</p>
          <p className="mt-2 text-xs text-slate-400">
            Shutdown: {scenario?.shutdownActive ? 'Active' : risk?.shutdownRequired ? 'Required' : 'Standby'}
          </p>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-4">
        <ScoreTile label="Plant safety score" value={`${(safetyMetrics?.overallPlantSafetyScore ?? risk?.score ?? 100).toFixed(1)}`} />
        <ScoreTile label="Detection accuracy" value={`${(safetyMetrics?.hazardDetectionAccuracy ?? 98.5).toFixed(1)}%`} />
        <ScoreTile label="Response time" value={`${(safetyMetrics?.emergencyResponseTimeSec ?? 0.8).toFixed(2)} s`} />
        <ScoreTile label="Sensor availability" value={`${(safetyMetrics?.sensorAvailability ?? 100).toFixed(1)}%`} />
      </div>
    </section>
  )
}
