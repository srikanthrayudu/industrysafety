import type { NetworkState } from '../types/simulator'

type IncidentReportProps = {
  state: NetworkState
}

function buildReport(state: NetworkState) {
  const latestLog = state.logs[state.logs.length - 1]
  return {
    generatedAt: new Date().toISOString(),
    project: state.project?.name ?? 'Smart Industrial Safety Monitoring and Emergency Response Simulator',
    focus: state.project?.focus ?? 'Industrial Safety Engineering',
    plant: state.plant,
    summary: {
      latestEvent: latestLog?.event ?? 'No event recorded',
      riskLevel: state.risk?.level ?? 'GREEN',
      plantSafetyScore: state.risk?.score ?? 100,
      safetyLevel: state.safety?.level ?? 'normal',
      activeRoute: state.routes.current.join(' -> ') || 'No active route',
      backupRouteActive: state.routes.backupActive,
    },
    sensors: state.sensors,
    hazards: state.hazards,
    emergency: state.emergency,
    communication: state.communication,
    safetyMetrics: state.safetyMetrics,
    metrics: state.metrics,
    scenario: state.scenario,
    thresholds: state.thresholds,
    violations: state.safety?.violations ?? [],
    recentAlerts: state.alerts.slice(-10),
    recentLogs: state.logs.slice(-20),
  }
}

export default function IncidentReport({ state }: IncidentReportProps) {
  const downloadReport = () => {
    const report = buildReport(state)
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `industrial-safety-report-${Date.now()}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-sm font-semibold text-slate-100">Incident Summary Report</h3>
          <p className="mt-1 text-xs text-slate-400">Exports sensors, hazards, actions, communication, metrics, and logs.</p>
        </div>
        <button onClick={downloadReport} className="rounded bg-cyan-700 px-3 py-2 text-xs font-semibold text-white hover:bg-cyan-600">
          Export Report
        </button>
      </div>
    </section>
  )
}
