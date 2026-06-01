import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import type { HistoryEntry, Metrics } from '../types/simulator'

type ReliabilityChartProps = {
  history: HistoryEntry[]
  metrics: Metrics
}

export default function ReliabilityChart({ history, metrics }: ReliabilityChartProps) {
  const nodePieData = [
    { name: 'Active Nodes', value: metrics.activeNodes, fill: '#10b981' },
    { name: 'Failed Nodes', value: metrics.failedNodes, fill: '#ef4444' },
  ]

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
      <div className="rounded-md border border-slate-700 bg-slate-800 p-3 xl:col-span-2">
        <h3 className="mb-2 text-sm font-semibold text-slate-100">Plant Safety and Communication Over Time</h3>
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={history.slice(-30)}>
              <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} unit="%" />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="reliability" name="Communication %" stroke="#38bdf8" strokeWidth={2} dot={false} />
              <Line type="monotone" dataKey="riskScore" name="Safety Score" stroke="#10b981" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-md border border-slate-700 bg-slate-800 p-3">
        <h3 className="mb-2 text-sm font-semibold text-slate-100">Node Status</h3>
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={nodePieData} dataKey="value" nameKey="name" outerRadius={70} label />
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-md border border-slate-700 bg-slate-800 p-3 xl:col-span-3">
        <h3 className="mb-2 text-sm font-semibold text-slate-100">Missed Readings and Response Delay</h3>
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={history.slice(-30)}>
              <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
              <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis yAxisId="left" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="packetLossPercent" name="Packet Loss %" fill="#f59e0b" />
              <Bar yAxisId="right" dataKey="delayMs" name="Delay (ms)" fill="#38bdf8" />
              <Bar yAxisId="left" dataKey="activeHazards" name="Active Hazards" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
