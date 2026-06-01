import { useEffect, useState } from 'react'
import axios from 'axios'

import Dashboard from './pages/Dashboard'
import Home from './pages/Home'
import Logs from './pages/Logs'
import ProjectInfo from './pages/ProjectInfo'
import type { NetworkState } from './types/simulator'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

type PageTab = 'home' | 'dashboard' | 'explain' | 'logs'

function createEmptyState(): NetworkState {
  return {
    project: {
      name: 'Smart Industrial Safety Monitoring and Emergency Response Simulator',
      focus: 'Industrial Safety Engineering',
      communicationRole: 'Communication reliability is modeled as a safety support layer.',
    },
    plant: {
      name: 'Integrated Hazardous Process Facility',
      processArea: 'Multi-domain training simulator',
      mode: 'Normal Operation',
      activeScenario: 'Normal Operation',
      description: 'Chemical, nuclear, mining, oil and gas, and hazardous manufacturing safety training.',
    },
    sensors: [],
    hazards: [],
    risk: {
      level: 'GREEN',
      label: 'Normal',
      score: 100,
      drivers: [],
      hazardCount: 0,
      shutdownRequired: false,
      color: '#10b981',
    },
    emergency: {
      actions: [],
      shutdownActive: false,
      lastShutdownStatus: 'standby',
      responseMode: 'Automatic SIS response with operator visibility',
    },
    communication: {
      safetyCommunicationReliability: 100,
      alarmDeliverySuccessRate: 100,
      emergencyShutdownSuccessRate: 100,
      averageResponseDelayMs: 0,
      missedSensorReadings: 0,
      currentPath: [],
      backupRouteActive: false,
      alarmChannelSuppressed: false,
    },
    safetyMetrics: {
      overallPlantSafetyScore: 100,
      hazardDetectionAccuracy: 98.5,
      alarmDeliveryRate: 100,
      emergencyResponseTimeSec: 0.8,
      emergencyShutdownSuccessRate: 100,
      sensorAvailability: 100,
      communicationReliability: 100,
      meanTimeBetweenFailuresSec: 0,
      meanTimeToRecoverySec: 0,
    },
    scenarioCatalog: [],
    nodes: [],
    links: [],
    metrics: {
      packetsSent: 0,
      packetsReceived: 0,
      packetsLost: 0,
      packetLossPercent: 0,
      reliability: 100,
      communicationReliability: 100,
      safetyCommunicationReliability: 100,
      delayMs: 0,
      alarmDeliverySuccessRate: 100,
      emergencyShutdownSuccessRate: 100,
      plantSafetyScore: 100,
      sensorAvailability: 100,
      hazardDetectionAccuracy: 98.5,
      emergencyResponseTimeSec: 0.8,
      activeHazards: 0,
      activeNodes: 0,
      failedNodes: 0,
    },
    routes: { monitoredFlow: { from: 'A', to: 'E' }, primary: [], current: [], backupActive: false },
    alerts: [],
    logs: [],
    history: [],
    scenario: {
      alarmSuppressed: false,
      falseDataActive: false,
      dosActive: false,
      activeSafetyScenario: null,
      activeScenarioLabel: 'Normal Operation',
      scenarioTicksRemaining: 0,
      shutdownActive: false,
    },
    safety: {
      level: 'normal',
      violations: [],
      thresholdsMet: true,
    },
    thresholds: {
      minReliability: 99,
      maxDelayMs: 150,
      maxPacketLossPercent: 1,
    },
  }
}

export default function App() {
  const [page, setPage] = useState<PageTab>('dashboard')
  const [state, setState] = useState<NetworkState>(createEmptyState())
  const [loading, setLoading] = useState(true)

  const fetchStatus = async () => {
    const response = await axios.get<NetworkState>(`${API_BASE}/network/status`)
    setState(response.data)
  }

  useEffect(() => {
    let timerId: number
    const run = async () => {
      try {
        await fetchStatus()
      } catch (error) {
        console.error(error)
      } finally {
        setLoading(false)
      }
      timerId = window.setTimeout(run, 1000)
    }
    run()
    return () => window.clearTimeout(timerId)
  }, [])

  const postAction = async (endpoint: string, payload?: object) => {
    await axios.post(`${API_BASE}${endpoint}`, payload)
    await fetchStatus()
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-6 text-slate-100 sm:px-6">
      <div className="mx-auto max-w-7xl space-y-4">
        <header className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-700 bg-slate-900 p-4">
          <div>
            <h1 className="text-xl font-semibold">Smart Industrial Safety Monitoring and Emergency Response Simulator</h1>
            <p className="text-xs text-slate-400">SCADA-inspired hazard detection, emergency response, and safety communication reliability</p>
          </div>
          <nav className="flex items-center gap-2">
            <button
              onClick={() => setPage('home')}
              className={`rounded px-3 py-1.5 text-sm ${page === 'home' ? 'bg-emerald-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Home
            </button>
            <button
              onClick={() => setPage('dashboard')}
              className={`rounded px-3 py-1.5 text-sm ${
                page === 'dashboard' ? 'bg-emerald-600' : 'bg-slate-700 hover:bg-slate-600'
              }`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setPage('explain')}
              className={`rounded px-3 py-1.5 text-sm ${
                page === 'explain' ? 'bg-emerald-600' : 'bg-slate-700 hover:bg-slate-600'
              }`}
            >
              Analytics
            </button>
            <button
              onClick={() => setPage('logs')}
              className={`rounded px-3 py-1.5 text-sm ${page === 'logs' ? 'bg-emerald-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Incident Logs
            </button>
          </nav>
        </header>

        {loading ? (
          <section className="rounded-md border border-slate-700 bg-slate-800 p-6 text-sm text-slate-300">
            Loading simulation status...
          </section>
        ) : null}

        {!loading && page === 'home' ? <Home onStart={() => setPage('dashboard')} /> : null}
        {!loading && page === 'dashboard' ? (
          <Dashboard
            state={state}
            onFail={(nodeId) => postAction('/simulate/failure', { nodeId })}
            onRestore={(nodeId) => postAction('/simulate/restore', { nodeId })}
            onFailLink={(source, target) => postAction('/simulate/link-failure', { source, target })}
            onRestoreLink={(source, target) => postAction('/simulate/link-restore', { source, target })}
            onScenario={(event, payload) => postAction('/api/simulate', { event, ...payload })}
            onReset={() => postAction('/reset')}
          />
        ) : null}
        {!loading && page === 'explain' ? <ProjectInfo state={state} /> : null}
        {!loading && page === 'logs' ? <Logs logs={state.logs} /> : null}
      </div>
    </main>
  )
}
