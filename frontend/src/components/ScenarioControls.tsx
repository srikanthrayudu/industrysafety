import type { NetworkLink, ScenarioState } from '../types/simulator'

type ScenarioControlsProps = {
  links: NetworkLink[]
  scenario?: ScenarioState
  onScenario: (event: string, payload?: Record<string, unknown>) => void
  onFailLink: (source: string, target: string) => void
  onRestoreLink: (source: string, target: string) => void
}

type ScenarioButton = {
  label: string
  event: string
  payload?: Record<string, unknown>
  tone: string
}

const scenarioButtons: ScenarioButton[] = [
  { label: 'Packet Loss', event: 'packet_loss', payload: { rate: 0.08 }, tone: 'bg-amber-600 hover:bg-amber-500' },
  { label: 'High Latency', event: 'latency', payload: { latencyMs: 140 }, tone: 'bg-sky-600 hover:bg-sky-500' },
  { label: 'DoS Flood', event: 'dos', payload: { durationTicks: 12 }, tone: 'bg-red-600 hover:bg-red-500' },
  { label: 'False Data', event: 'false_data', payload: { value: 41 }, tone: 'bg-fuchsia-700 hover:bg-fuchsia-600' },
  { label: 'ESD Command', event: 'esd_command', tone: 'bg-emerald-600 hover:bg-emerald-500' },
  { label: 'ESD Failure', event: 'esd_failure', tone: 'bg-rose-700 hover:bg-rose-600' },
]

const presetScenarios = [
  {
    label: 'PLC Failure',
    actions: [{ event: 'fail_node', payload: { nodeId: 'B' } }],
  },
  {
    label: 'Network Congestion',
    actions: [
      { event: 'latency', payload: { latencyMs: 160 } },
      { event: 'packet_loss', payload: { rate: 0.04 } },
    ],
  },
  {
    label: 'Cyber Attack',
    actions: [
      { event: 'dos', payload: { durationTicks: 12 } },
      { event: 'false_data', payload: { value: 41 } },
      { event: 'alarm_suppression', payload: { enabled: true } },
    ],
  },
  {
    label: 'Emergency Shutdown Test',
    actions: [{ event: 'esd_command', payload: {} }],
  },
  {
    label: 'Full Recovery',
    actions: [{ event: 'reset_conditions', payload: {} }],
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
  onScenario,
  onFailLink,
  onRestoreLink,
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
          <h3 className="text-sm font-semibold text-slate-100">Safety Scenario Controls</h3>
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
              className={`min-h-10 rounded px-3 py-2 text-xs font-semibold text-white ${button.tone}`}
            >
              {button.label}
            </button>
          ))}
        </div>

        <div className="mt-4 border-t border-slate-700 pt-3">
          <h4 className="text-xs font-semibold uppercase text-slate-400">Scenario Presets</h4>
          <div className="mt-2 grid grid-cols-2 gap-2 md:grid-cols-5">
            {presetScenarios.map((preset) => (
              <button
                key={preset.label}
                onClick={() => runPreset(preset.actions)}
                className="min-h-10 rounded bg-indigo-700 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-600"
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
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
        </div>
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
