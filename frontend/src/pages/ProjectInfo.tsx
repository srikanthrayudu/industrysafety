import type { NetworkState } from '../types/simulator'

type ProjectInfoProps = {
  state: NetworkState
}

const scenarioRows = [
  ['Chemical Leak', 'Detects toxic gas and pressure rise, then triggers siren, valve isolation, and operator notification.'],
  ['Radiation Spike', 'Raises nuclear safety risk and validates containment plus emergency shutdown behavior.'],
  ['Methane Explosion Risk', 'Models mine gas buildup with low oxygen and ventilation/evacuation response.'],
  ['PLC Failure During Emergency', 'Shows how a control node failure increases process risk during a live hazard.'],
  ['Communication Loss During Shutdown', 'Demonstrates delayed or failed shutdown delivery as a safety escalation layer.'],
]

export default function ProjectInfo({ state }: ProjectInfoProps) {
  return (
    <section className="space-y-4">
      <div className="rounded-md border border-slate-700 bg-slate-800 p-5">
        <h2 className="text-xl font-semibold text-slate-100">Safety Engineering Alignment</h2>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-300">
          This system is positioned as an industrial safety and emergency response simulator for chemical processing,
          nuclear safety, mining operations, oil and gas, and hazardous manufacturing. Communication reliability remains
          visible because alarms and shutdown commands must reach PLC, SIS, SCADA, and emergency operation nodes.
        </p>
        <p className="mt-3 text-xs text-slate-400">
          Current state: {state.risk?.level ?? 'GREEN'} risk / {state.sensors?.length ?? 0} sensors / {state.hazards?.length ?? 0} active hazards.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-100">Safety Sensors</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Sensors simulate temperature, pressure, toxic gas, radiation, methane, smoke, oxygen, and humidity with
            realistic industrial ranges and threshold-based risk levels.
          </p>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-100">Risk Engine</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            The backend calculates GREEN, YELLOW, ORANGE, RED, and BLACK states from sensor thresholds, node failures,
            communication delay, alarm delivery, and shutdown success.
          </p>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-100">Emergency Response</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Emergency actions include alarms, valve isolation, ventilation, evacuation, containment, and ESD command
            simulation with success and failure tracking.
          </p>
        </div>
      </div>

      <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
        <h3 className="text-sm font-semibold text-slate-100">Scenario Purpose</h3>
        <div className="mt-3 overflow-hidden rounded border border-slate-700">
          {scenarioRows.map(([name, purpose]) => (
            <div key={name} className="grid grid-cols-1 gap-2 border-b border-slate-700 px-4 py-3 last:border-b-0 md:grid-cols-[220px_1fr]">
              <span className="text-sm font-medium text-slate-100">{name}</span>
              <span className="text-sm text-slate-300">{purpose}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
