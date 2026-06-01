import AlertPanel from '../components/AlertPanel'
import CommunicationHealth from '../components/CommunicationHealth'
import EmergencyActions from '../components/EmergencyActions'
import HazardDetectionPanel from '../components/HazardDetectionPanel'
import IncidentReport from '../components/IncidentReport'
import IncidentTimeline from '../components/IncidentTimeline'
import NetworkMap from '../components/NetworkMap'
import NodeCard from '../components/NodeCard'
import PlantOverview from '../components/PlantOverview'
import ReliabilityChart from '../components/ReliabilityChart'
import RiskMeter from '../components/RiskMeter'
import ScenarioControls from '../components/ScenarioControls'
import SensorPanel from '../components/SensorPanel'
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
  const alarmRate = state.safetyMetrics?.alarmDeliveryRate ?? state.metrics.alarmDeliverySuccessRate ?? 100
  const shutdownRate = state.safetyMetrics?.emergencyShutdownSuccessRate ?? state.metrics.emergencyShutdownSuccessRate ?? 100
  const safetyScore = state.safetyMetrics?.overallPlantSafetyScore ?? state.risk?.score ?? state.metrics.plantSafetyScore ?? 100
  const communicationReliability = state.communication?.safetyCommunicationReliability ?? state.metrics.reliability

  return (
    <section className="space-y-4">
      <PlantOverview plant={state.plant} risk={state.risk} safetyMetrics={state.safetyMetrics} scenario={state.scenario} />

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <MetricTile label="Plant Safety Score" value={safetyScore.toFixed(1)} />
        <MetricTile label="Active Hazards" value={state.hazards?.length ?? state.metrics.activeHazards ?? 0} />
        <MetricTile label="Alarm Delivery" value={`${alarmRate.toFixed(2)}%`} />
        <MetricTile label="Shutdown Success" value={`${shutdownRate.toFixed(2)}%`} />
        <MetricTile label="Safety Comms" value={`${communicationReliability.toFixed(2)}%`} />
      </div>

      <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        <MetricTile label="Active Nodes" value={state.metrics.activeNodes} />
        <MetricTile label="Failed Nodes" value={state.metrics.failedNodes} />
        <MetricTile label="Missed Readings" value={state.metrics.packetsLost} />
        <MetricTile label="Response Delay" value={`${state.metrics.delayMs} ms`} />
        <MetricTile label="MTBF" value={`${state.metrics.mtbfSec ?? 0} s`} />
        <MetricTile label="MTTR" value={`${state.metrics.mttrSec ?? 0} s`} />
      </div>

      <ScenarioControls
        links={state.links}
        scenario={state.scenario}
        scenarioCatalog={state.scenarioCatalog}
        onScenario={onScenario}
        onFailLink={onFailLink}
        onRestoreLink={onRestoreLink}
        onReset={onReset}
      />

      <SensorPanel sensors={state.sensors} />

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[0.9fr_1.1fr_1fr]">
        <RiskMeter risk={state.risk} />
        <HazardDetectionPanel hazards={state.hazards} />
        <CommunicationHealth communication={state.communication} metrics={state.metrics} routes={state.routes} />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.35fr_1fr]">
        <NetworkMap nodes={state.nodes} links={state.links} routes={state.routes} />
        <EmergencyActions emergency={state.emergency} />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-700 bg-slate-800 p-4">
        <div className="space-y-1 text-sm text-slate-200">
          <div>Current Path: {formatPath(state.routes.current)}</div>
          <div className="text-xs text-slate-400">Network reliability remains visible as a supporting safety metric.</div>
        </div>
        <button onClick={onReset} className="rounded bg-slate-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-slate-500">
          Reset Simulator
        </button>
      </div>

      <div>
        <h3 className="mb-3 text-sm font-semibold text-slate-100">Safety System Nodes</h3>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-5">
          {state.nodes.map((node) => (
            <NodeCard key={node.id} node={node} onFail={onFail} onRestore={onRestore} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-5">
        <MetricTile label="Packet Loss" value={`${state.metrics.packetLossPercent.toFixed(2)}%`} />
        <MetricTile label="Throughput" value={`${state.metrics.throughputPps ?? 0} pps`} />
        <MetricTile label="Packets Sent" value={state.metrics.packetsSent} />
        <MetricTile label="ESD Success" value={state.metrics.esdSuccesses ?? 0} />
        <MetricTile label="ESD Failure" value={state.metrics.esdFailures ?? 0} />
      </div>

      <ReliabilityChart history={state.history} metrics={state.metrics} />
      <IncidentTimeline logs={state.logs} alerts={state.alerts} />
      <IncidentReport state={state} />
      <AlertPanel alerts={state.alerts} />
    </section>
  )
}
