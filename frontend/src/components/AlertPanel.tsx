// React import not required with new JSX transform

export default function AlertPanel({ alerts }: { alerts: { ts: string; msg: string }[] }) {
  return (
    <div style={{ maxHeight: 220, overflow: 'auto', padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 }}>
      <h3 style={{ margin: '4px 0 8px' }}>Alerts</h3>
      {alerts.length === 0 && <div style={{ color: '#6B7280' }}>No alerts</div>}
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {alerts.map((a, i) => (
          <li key={i} style={{ padding: '6px 4px', borderBottom: '1px solid #f3f4f6' }}>
            <div style={{ fontSize: 13, color: '#111827' }}>{a.msg}</div>
            <div style={{ fontSize: 11, color: '#6B7280' }}>{a.ts}</div>
          </li>
        ))}
      </ul>
    </div>
  )
}

