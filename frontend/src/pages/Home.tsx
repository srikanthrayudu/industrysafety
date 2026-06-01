type HomeProps = {
  onStart: () => void
}

export default function Home({ onStart }: HomeProps) {
  return (
    <section className="rounded-md border border-slate-700 bg-slate-800 p-8">
      <h2 className="text-2xl font-semibold text-slate-100">Smart Industrial Safety Monitoring and Emergency Response Simulator</h2>
      <p className="mt-4 max-w-3xl text-sm text-slate-300">
        This simulation monitors industrial safety sensors, detects abnormal process conditions, computes GREEN to
        BLACK risk levels, triggers emergency actions, and shows how communication reliability affects alarm and
        shutdown delivery.
      </p>
      <button
        onClick={onStart}
        className="mt-6 rounded bg-emerald-600 px-5 py-2 text-sm font-semibold text-white hover:bg-emerald-500"
      >
        Open Dashboard
      </button>
    </section>
  )
}
