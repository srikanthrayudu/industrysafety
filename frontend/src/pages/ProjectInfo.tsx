import type { NetworkState } from '../types/simulator'

type ProjectInfoProps = {
  state: NetworkState
}

const scenarioRows = [
  ['PLC Failure', 'Validates whether traffic fails over when the primary control path is interrupted.'],
  ['Network Congestion', 'Raises delay and packet loss to show degraded communication reliability.'],
  ['Cyber Attack', 'Combines DoS, false data, and alarm suppression to model hostile operating conditions.'],
  ['Emergency Shutdown Test', 'Checks whether an ESD command can reach the control room over the active route.'],
  ['Full Recovery', 'Restores communication conditions after a fault or attack scenario.'],
]

export default function ProjectInfo({ state }: ProjectInfoProps) {
  return (
    <section className="space-y-4">
      <div className="rounded-md border border-slate-700 bg-slate-800 p-5">
        <h2 className="text-xl font-semibold text-slate-100">Project Alignment</h2>
        <p className="mt-3 max-w-4xl text-sm leading-6 text-slate-300">
          This system models an industrial communication network where sensor data and safety commands must reach
          control equipment reliably. The monitored flow is {state.routes.monitoredFlow.from} to {state.routes.monitoredFlow.to},
          with a primary path and a redundant backup path used during faults.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-100">Industrial Network</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            Nodes represent sensor, PLC, SIS controller, backup gateway, and SCADA/control-room roles. Links include
            protocol labels such as Modbus TCP, Profinet, OPC UA, MQTT, and Industrial Ethernet.
          </p>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-100">Reliability Metrics</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            The simulator tracks reliability, packet loss, latency, throughput, MTBF, MTTR, route failover, alerts, and
            event logs while packets move across active network paths.
          </p>
        </div>
        <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
          <h3 className="text-sm font-semibold text-slate-100">Safety-Critical Behavior</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">
            ESD command delivery, false sensor data, alarm suppression, DoS traffic, and configured safety thresholds
            connect the communication model to safety-critical industrial operation.
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
