// React import not required with new JSX transform
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'

export default function ReliabilityChart({ data }: { data: { time: string; reliability: number }[] }) {
  return (
    <div style={{ width: '100%', height: 220 }}>
      <ResponsiveContainer>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" hide={data.length > 8 ? true : false} />
          <YAxis domain={[0, 100]} unit="%" />
          <Tooltip />
          <Line type="monotone" dataKey="reliability" stroke="#06b6d4" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

