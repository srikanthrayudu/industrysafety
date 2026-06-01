import { useEffect, useState, useRef } from 'react'
import axios from 'axios'
import NetworkMap from './components/NetworkMap'
import ReliabilityChart from './components/ReliabilityChart'
import AlertPanel from './components/AlertPanel'
import MQTTPanel from './components/MQTTPanel'

type N = { id: string; label: string; status: string }
type L = { source: string; target: string; active: boolean }
type RoutesType = Record<string, { primary?: string[]; current?: string[]; rerouted?: boolean }>

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000'

function App() {
  const [nodes, setNodes] = useState<N[]>([])
  const [links, setLinks] = useState<L[]>([])
  const [metrics, setMetrics] = useState<{ packetsSent: number; packetsLost: number; reliability: number } | null>(null)
  const [alerts, setAlerts] = useState<{ ts: string; msg: string }[]>([])
  const [routes, setRoutes] = useState<RoutesType | undefined>(undefined)
  const [chartData, setChartData] = useState<{ time: string; reliability: number }[]>([])
  const lastNodesRef = useRef<Record<string, string>>({})
  type MQTTMsg = { ts: number; topic: string; message: unknown }
  const [mqttMsgs, setMQTTMsgs] = useState<MQTTMsg[]>([])
  const [subscribedTopics, setSubscribedTopics] = useState<string[]>(['sim/metrics'])
  const [newTopic, setNewTopic] = useState('')

  // Replace polling with SSE subscription
  useEffect(() => {
    const es = new EventSource(`${API_BASE}/events`)
    // listen for named events: 'state' and 'mqtt'
    es.addEventListener('state', (ev: MessageEvent) => {
      try {
        const raw = (ev as MessageEvent).data as string
        const data = JSON.parse(raw)
        const prevNodes = lastNodesRef.current
        setNodes(data.nodes)
        setLinks(data.links)
        setMetrics(data.metrics)
        setRoutes(data.routes)

        // update chart
        const now = new Date().toLocaleTimeString()
        const point = { time: now, reliability: Math.round((data.metrics.reliability + Number.EPSILON) * 100) / 100 }
        setChartData((c) => [...c.slice(-49), point])

        // alerts for node status change
        const newAlerts: { ts: string; msg: string }[] = []
        for (const n of data.nodes) {
          const prev = prevNodes[n.id]
          if (prev && prev !== n.status) {
            newAlerts.push({ ts: now, msg: `Node ${n.id} (${n.label}) is now ${n.status}` })
          }
        }
        if (newAlerts.length) setAlerts((s) => [...newAlerts, ...s].slice(0, 200))
        // update lastNodesRef
        const nodeMap: Record<string, string> = {}
        for (const n of data.nodes) {
          nodeMap[n.id] = n.status
        }
        lastNodesRef.current = nodeMap
      } catch (err) {
        console.error('SSE parse error', err)
      }
    })
    es.addEventListener('mqtt', (ev: MessageEvent) => {
      try {
        const raw = (ev as MessageEvent).data as string
        const m = JSON.parse(raw) as MQTTMsg
        setMQTTMsgs((prev) => [...prev.slice(-199), m])
      } catch {
        // ignore parse errors
      }
    })
    es.onerror = (e) => {
      console.warn('SSE connection error', e)
      es.close()
      // fallback: try reconnect after a short delay
      setTimeout(() => {
        // reinstantiate by rerunning effect
        window.location.reload()
      }, 3000)
    }
    return () => es.close()
  }, [])

  async function failNode(nodeId: string) {
    try {
      await axios.post(`${API_BASE}/simulate/failure`, { nodeId })
      // SSE will update state
    } catch (err) {
      console.error(err)
    }
  }

  async function restoreNode(nodeId: string) {
    try {
      await axios.post(`${API_BASE}/simulate/restore`, { nodeId })
    } catch (err) {
      console.error(err)
    }
  }

  async function resetNetwork() {
    try {
      await axios.post(`${API_BASE}/reset`)
      setChartData([])
      setAlerts([])
    } catch (err) {
      console.error(err)
    }
  }

  async function subscribeTopic(topic: string) {
    try {
      await fetch(`${API_BASE}/mqtt/subscribe`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic }) })
      setSubscribedTopics((s) => (s.includes(topic) ? s : [...s, topic]))
    } catch (e) {
      console.error(e)
    }
  }

  async function unsubscribeTopic(topic: string) {
    try {
      await fetch(`${API_BASE}/mqtt/unsubscribe`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ topic }) })
      setSubscribedTopics((s) => s.filter((t) => t !== topic))
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <div className="p-6 min-h-screen bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      <div className="max-w-6xl mx-auto">
        <header className="mb-6">
          <h1 className="text-2xl font-semibold">Industrial Network Reliability Simulator</h1>
        </header>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="col-span-1">
            <NetworkMap nodes={nodes} links={links} routes={routes} />
          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <div className="flex flex-wrap gap-2 mt-3">
              {nodes.map((n) => (
                n.status === 'active' ? (
                  <button key={n.id} onClick={() => failNode(n.id)} className="px-3 py-1 rounded bg-red-500 text-white text-sm">
                    Fail {n.id}
                  </button>
                ) : (
                  <button key={n.id} onClick={() => restoreNode(n.id)} className="px-3 py-1 rounded bg-green-600 text-white text-sm">
                    Restore {n.id}
                  </button>
                )
              ))}
              <button onClick={resetNetwork} className="px-3 py-1 rounded bg-gray-600 text-white text-sm">Reset</button>
            </div>
          </div>
          </div>
          <div className="col-span-2 space-y-4">
            <div className="bg-white dark:bg-slate-800 p-4 rounded shadow">
              <h2 className="font-medium mb-2">Metrics</h2>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>Packets sent: <span className="font-semibold">{metrics?.packetsSent ?? '-'}</span></div>
                <div>Packets lost: <span className="font-semibold">{metrics?.packetsLost ?? '-'}</span></div>
                <div>Reliability: <span className="font-semibold">{metrics ? `${metrics.reliability.toFixed(2)}%` : '-'}</span></div>
              </div>
            </div>

            <div className="bg-white dark:bg-slate-800 p-4 rounded shadow">
              <ReliabilityChart data={chartData} />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white dark:bg-slate-800 p-4 rounded shadow">
                <AlertPanel alerts={alerts} />
              </div>
                      <div className="bg-white dark:bg-slate-800 p-4 rounded shadow">
                        <div className="mb-3 flex gap-2">
                          <input value={newTopic} onChange={(e) => setNewTopic(e.target.value)} placeholder="topic (e.g. sim/metrics)" className="flex-1 border rounded px-2 py-1" />
                          <button onClick={() => { if (newTopic.trim()) { subscribeTopic(newTopic.trim()); setNewTopic('') } }} className="px-3 py-1 rounded bg-blue-600 text-white">Subscribe</button>
                        </div>
                        <div className="mb-2 text-sm">Subscribed topics: {subscribedTopics.map(t => (
                          <button key={t} onClick={() => unsubscribeTopic(t)} className="ml-2 px-2 py-1 text-xs rounded bg-gray-200 dark:bg-slate-700">{t} ×</button>
                        ))}</div>
                        <MQTTPanel msgs={mqttMsgs.filter(m => subscribedTopics.includes(m.topic))} />
                      </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
