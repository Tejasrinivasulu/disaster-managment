import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'

export default function FieldReportsPage() {
  const [reports, setReports] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/field-reports')
      .then(({ data }) => setReports(data))
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="mx-auto max-w-3xl space-y-4 pb-20 md:pb-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-teal-700">Field Team</p>
        <h2 className="font-display text-xl font-bold">My Field Reports</h2>
        <p className="text-sm text-command-600">Submitted ground reports (population, damage, notes).</p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      {reports.length === 0 ? (
        <div className="card text-sm text-command-500">No reports yet. Submit one from the Field Dashboard.</div>
      ) : (
        reports.map((r) => (
          <div key={r.id} className="card space-y-1 text-sm">
            <div className="flex justify-between gap-2">
              <p className="font-semibold">Report #{r.id} · Zone {r.zone_id}</p>
              {r.severity && <StatusBadge value={r.severity} />}
            </div>
            <p>Population: {r.population_affected ?? '—'} · Building damage: {r.building_damage_pct ?? '—'}%</p>
            <p className="text-command-600">{r.notes || 'No notes'}</p>
            <p className="text-xs text-command-400">{r.created_at ? new Date(r.created_at).toLocaleString() : ''}</p>
          </div>
        ))
      )}
    </div>
  )
}
