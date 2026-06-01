import type { LogEntry } from '../types/simulator'

type LogsProps = {
  logs: LogEntry[]
}

export default function Logs({ logs }: LogsProps) {
  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-4">
      <h2 className="text-lg font-semibold text-slate-100">System Logs</h2>
      <div className="mt-4 max-h-[540px] overflow-y-auto rounded border border-slate-700">
        {logs.length === 0 && <p className="p-4 text-sm text-slate-400">No logs yet.</p>}
        {logs
          .slice()
          .reverse()
          .map((entry, index) => (
            <div key={`${entry.time}-${index}`} className="border-b border-slate-700 px-4 py-2 text-sm text-slate-200">
              <span className="mr-3 text-xs text-slate-400">{entry.time}</span>
              <span>{entry.event}</span>
            </div>
          ))}
      </div>
    </section>
  )
}
