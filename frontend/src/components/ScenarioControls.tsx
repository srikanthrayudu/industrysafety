import type { NetworkLink, ScenarioCatalogItem, ScenarioState } from '../types/simulator'

type ScenarioControlsProps = {
  links: NetworkLink[]
  scenario?: ScenarioState
  scenarioCatalog?: ScenarioCatalogItem[]
  onScenario: (event: string, payload?: Record<string, unknown>) => void
  onFailLink: (source: string, target: string) => void
  onRestoreLink: (source: string, target: string) => void
  onReset: () => void
}

type ScenarioButton = {
  label: string
  event: string
  payload?: Record<string, unknown>
  tone: string
}

const scenarioButtons: ScenarioButton[] = [
  { label: 'Chemical Leak', event: 'chemical_leak', tone: 'bg-orange-600 hover:bg-orange-500' },
  { label: 'Radiation Spike', event: 'radiation_spike', tone: 'bg-red-700 hover:bg-red-600' },
  { label: 'Methane Risk', event: 'methane_explosion', tone: 'bg-yellow-600 hover:bg-yellow-500' },
  { label: 'Reactor Heat', event: 'reactor_overheat', tone: 'bg-rose-700 hover:bg-rose-600' },
  { label: 'PLC Emergency', event: 'plc_failure_emergency', tone: 'bg-indigo-700 hover:bg-indigo-600' },
  { label: 'Comms Loss', event: 'communication_loss_shutdown', tone: 'bg-slate-600 hover:bg-slate-500' },
]

const presetScenarios = [
  {
    label: 'Cooling Failure',
    actions: [{ event: 'cooling_failure', payload: {} }],
  },
  {
    label: 'Tunnel Fire',
    actions: [{ event: 'tunnel_fire', payload: {} }],
  },
  {
    label: 'Oxygen Low',
    actions: [{ event: 'oxygen_deficiency', payload: {} }],
  },
  {
    label: 'Pipeline Fail',
    actions: [{ event: 'pipeline_failure', payload: {} }],
  },
  {
    label: 'Cyber Attack',
    actions: [
      { event: 'dos', payload: { durationTicks: 12 } },
      { event: 'false_data', payload: { value: 41 } },
      { event: 'alarm_suppression', payload: { enabled: true } },
    ],
  },
]

function ScenarioBadge({ active, label }: { active: boolean; label: string }) {
  return (
    <span
      className={`rounded border px-2 py-1 text-xs font-medium ${
        active ? 'border-red-400/40 bg-red-500/15 text-red-200' : 'border-slate-600 bg-slate-900 text-slate-300'
      }`}
    >
      {label}
    </span>
  )
}

export default function ScenarioControls({
  links,
  scenario,
  scenarioCatalog,
  onScenario,
  onFailLink,
  onRestoreLink,
  onReset,
}: ScenarioControlsProps) {
  const runPreset = (actions: { event: string; payload: Record<string, unknown> }[]) => {
    for (const action of actions) {
      onScenario(action.event, action.payload)
    }
  }

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.2fr_1fr]">
      <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Simulation Scenarios</h3>
            <p className="mt-1 text-xs text-slate-400">
              {scenario?.activeScenarioLabel ?? 'Normal Operation'}
              {scenario?.scenarioTicksRemaining ? ` / ${scenario.scenarioTicksRemaining}s remaining` : ''}
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <ScenarioBadge active={Boolean(scenario?.dosActive)} label="DoS" />
            <ScenarioBadge active={Boolean(scenario?.falseDataActive)} label="False Data" />
            <ScenarioBadge active={Boolean(scenario?.alarmSuppressed)} label="Alarm Suppressed" />
          </div>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-3">
          {scenarioButtons.map((button) => (
            <button
              key={button.label}
              onClick={() => onScenario(button.event, button.payload)}
              className={`min-h-10 rounded px-3 py-2 text-xs font-semibold leading-4 text-white ${button.tone}`}
            >
              {button.label}
            </button>
          ))}
        </div>

        <div className="mt-4 border-t border-slate-700 pt-3">
          <h4 className="text-xs font-semibold uppercase text-slate-400">Additional hazards</h4>
          <div className="mt-2 grid grid-cols-2 gap-2 md:grid-cols-5">
            {presetScenarios.map((preset) => (
              <button
                key={preset.label}
                onClick={() => runPreset(preset.actions)}
                className="min-h-10 rounded bg-cyan-800 px-3 py-2 text-xs font-semibold leading-4 text-white hover:bg-cyan-700"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={() => onScenario('packet_loss', { rate: 0.08 })}
            className="rounded bg-amber-700 px-3 py-2 text-xs font-semibold text-white hover:bg-amber-600"
          >
            Packet Loss
          </button>
          <button
            onClick={() => onScenario('latency', { latencyMs: 180 })}
            className="rounded bg-sky-700 px-3 py-2 text-xs font-semibold text-white hover:bg-sky-600"
          >
            High Latency
          </button>
          <button
            onClick={() => onScenario('esd_command')}
            className="rounded bg-emerald-700 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-600"
          >
            ESD Command
          </button>
          <button
            onClick={() => onScenario('esd_failure')}
            className="rounded bg-red-700 px-3 py-2 text-xs font-semibold text-white hover:bg-red-600"
          >
            ESD Failure
          </button>
          <button
            onClick={() => onScenario('alarm_suppression', { enabled: !scenario?.alarmSuppressed })}
            className="rounded bg-slate-600 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-500"
          >
            {scenario?.alarmSuppressed ? 'Restore Alarms' : 'Suppress Alarms'}
          </button>
          <button
            onClick={() => onScenario('reset_conditions')}
            className="rounded bg-slate-700 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-600"
          >
            Normalize Conditions
          </button>
          <button
            onClick={onReset}
            className="rounded bg-slate-500 px-3 py-2 text-xs font-semibold text-white hover:bg-slate-400"
          >
            Full Reset
          </button>
        </div>

        {scenarioCatalog?.length ? (
          <div className="mt-4 grid grid-cols-1 gap-2 border-t border-slate-700 pt-3 md:grid-cols-2">
            {scenarioCatalog.slice(0, 4).map((item) => (
              <div key={item.id} className="rounded border border-slate-700 bg-slate-950/70 px-3 py-2">
                <p className="text-xs font-semibold text-slate-200">{item.label}</p>
                <p className="mt-1 text-[11px] text-slate-500">{item.environment}</p>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
        <h3 className="text-sm font-semibold text-slate-100">Link Reliability Controls</h3>
        <div className="mt-3 max-h-56 space-y-2 overflow-y-auto pr-1">
          {links.map((link) => (
            <div
              key={link.id ?? `${link.source}-${link.target}`}
              className="flex items-center justify-between gap-3 rounded border border-slate-700 bg-slate-900 px-3 py-2"
            >
              <div>
                <p className="text-sm font-medium text-slate-100">
                  {link.source} - {link.target}
                </p>
                <p className="text-xs text-slate-400">
                  {link.protocol ?? 'Industrial Ethernet'} / {link.latency_ms ?? 0} ms / {(((link.loss_rate ?? 0) * 100)).toFixed(1)}
                  % loss
                </p>
              </div>
              <button
                onClick={() =>
                  link.active ? onFailLink(link.source, link.target) : onRestoreLink(link.source, link.target)
                }
                className={`rounded px-3 py-1.5 text-xs font-semibold text-white ${
                  link.active ? 'bg-red-600 hover:bg-red-500' : 'bg-emerald-600 hover:bg-emerald-500'
                }`}
              >
                {link.active ? 'Fail' : 'Restore'}
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}
