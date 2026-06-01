import AlertPanel from '../components/AlertPanel'
import IncidentReport from '../components/IncidentReport'
import NetworkMap from '../components/NetworkMap'
import NodeCard from '../components/NodeCard'
import ReliabilityChart from '../components/ReliabilityChart'
import ScenarioControls from '../components/ScenarioControls'
import SafetyStatusPanel from '../components/SafetyStatusPanel'
import type { NetworkState } from '../types/simulator'

type DashboardProps = {
  state: NetworkState
  onFail: (nodeId: string) => void
  onRestore: (nodeId: string) => void
  onFailLink: (source: string, target: string) => void
  onRestoreLink: (source: string, target: string) => void
  onScenario: (event: string, payload?: Record<string, unknown>) => void
  onReset: () => void
}

function MetricTile({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border border-slate-700 bg-slate-800 p-3">
      <p className="text-xs text-slate-400">{label}</p>
      <p className="mt-1 text-xl font-semibold text-slate-100">{value}</p>
    </div>
  )
}

function formatPath(path: string[]) {
  return path.length > 0 ? path.join(' -> ') : 'No active route'
}

export default function Dashboard({
  state,
  onFail,
  onRestore,
  onFailLink,
  onRestoreLink,
  onScenario,
  onReset,
}: DashboardProps) {
  const routeState = state.routes.backupActive ? 'Backup Route Activated' : 'Primary Route Active'
  const sensor = state.nodes.find((node) => node.id === 'A')

  return (
    <section className="space-y-4">
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <MetricTile label="Active Nodes" value={state.metrics.activeNodes} />
        <MetricTile label="Failed Nodes" value={state.metrics.failedNodes} />
        <MetricTile label="Reliability" value={`${state.metrics.reliability.toFixed(2)}%`} />
        <MetricTile label="Packet Loss" value={`${state.metrics.packetLossPercent.toFixed(2)}%`} />
        <MetricTile label="Delay" value={`${state.metrics.delayMs} ms`} />
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <MetricTile label="Throughput" value={`${state.metrics.throughputPps ?? 0} pps`} />
        <MetricTile label="MTBF" value={`${state.metrics.mtbfSec ?? 0} s`} />
        <MetricTile label="MTTR" value={`${state.metrics.mttrSec ?? 0} s`} />
        <MetricTile label="ESD Success" value={state.metrics.esdSuccesses ?? 0} />
        <MetricTile label="ESD Failure" value={state.metrics.esdFailures ?? 0} />
      </div>

      <div className="rounded-md border border-slate-700 bg-slate-800 p-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="space-y-1 text-sm text-slate-200">
            <div>Route State: {routeState}</div>
            <div className="text-xs text-slate-400">Current Path: {formatPath(state.routes.current)}</div>
            <div className="text-xs text-slate-400">
              Sensor A: {sensor?.reading ?? '--'} {sensor?.unit ?? ''}
            </div>
          </div>
          <button onClick={onReset} className="rounded bg-slate-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-500">
            Reset Network
          </button>
        </div>
      </div>

      <ScenarioControls
        links={state.links}
        scenario={state.scenario}
        onScenario={onScenario}
        onFailLink={onFailLink}
        onRestoreLink={onRestoreLink}
      />

      <SafetyStatusPanel metrics={state.metrics} safety={state.safety} thresholds={state.thresholds} />

      <NetworkMap nodes={state.nodes} links={state.links} routes={state.routes} />

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-5">
        {state.nodes.map((node) => (
          <NodeCard key={node.id} node={node} onFail={onFail} onRestore={onRestore} />
        ))}
      </div>

      <ReliabilityChart history={state.history} metrics={state.metrics} />
      <IncidentReport state={state} />
      <AlertPanel alerts={state.alerts} />
    </section>
  )
}
