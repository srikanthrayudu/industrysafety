import { useEffect, useState } from 'react'
import axios from 'axios'

import Dashboard from './pages/Dashboard'
import Home from './pages/Home'
import Logs from './pages/Logs'
import type { NetworkState } from './types/simulator'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

type PageTab = 'home' | 'dashboard' | 'logs'

function createEmptyState(): NetworkState {
  return {
    nodes: [],
    links: [],
    metrics: {
      packetsSent: 0,
      packetsReceived: 0,
      packetsLost: 0,
      packetLossPercent: 0,
      reliability: 100,
      delayMs: 0,
      activeNodes: 0,
      failedNodes: 0,
    },
    routes: { monitoredFlow: { from: 'A', to: 'E' }, primary: [], current: [], backupActive: false },
    alerts: [],
    logs: [],
    history: [],
  }
}

export default function App() {
  const [page, setPage] = useState<PageTab>('home')
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
    <main className="min-h-screen bg-slate-900 px-4 py-6 text-slate-100 sm:px-6">
      <div className="mx-auto max-w-7xl space-y-4">
        <header className="flex flex-wrap items-center justify-between gap-3 rounded-md border border-slate-700 bg-slate-800 p-4">
          <div>
            <h1 className="text-xl font-semibold">SCADA Monitoring Interface</h1>
            <p className="text-xs text-slate-400">Fault Injection and Redundant Communication Path Simulation</p>
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
              onClick={() => setPage('logs')}
              className={`rounded px-3 py-1.5 text-sm ${page === 'logs' ? 'bg-emerald-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Logs
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
            onReset={() => postAction('/reset')}
          />
        ) : null}
        {!loading && page === 'logs' ? <Logs logs={state.logs} /> : null}
      </div>
    </main>
  )
}
