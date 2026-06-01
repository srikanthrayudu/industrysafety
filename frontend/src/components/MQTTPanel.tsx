export default function MQTTPanel({ msgs }: { msgs: { ts: number; topic: string; message: unknown }[] }) {
  return (
    <div className="p-2 border rounded bg-white dark:bg-slate-800">
      <h3 className="font-semibold mb-2">MQTT messages (sim/metrics)</h3>
      <div className="max-h-40 overflow-auto text-xs">
        {msgs.length === 0 && <div className="text-gray-500">No messages</div>}
        <ul className="space-y-1">
          {msgs.map((m, i) => (
            <li key={i} className="p-1 border-b last:border-b-0">
              <div className="text-xs text-slate-500">{new Date(m.ts * 1000).toLocaleTimeString()} · {m.topic}</div>
              <pre className="whitespace-pre-wrap">{JSON.stringify(m.message)}</pre>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
