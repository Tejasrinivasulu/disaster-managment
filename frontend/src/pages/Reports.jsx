import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import { formatNumber } from '../utils/format'

export default function Reports() {
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')
  const [exporting, setExporting] = useState('')

  useEffect(() => {
    api.get('/reports/summary')
      .then(({ data }) => setSummary(data))
      .catch((err) => setError(err.message))
  }, [])

  async function downloadExport(path, filename, label) {
    setExporting(label)
    setError('')
    try {
      const res = await api.get(path, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(err.message)
    } finally {
      setExporting('')
    }
  }

  if (error && !summary) {
    return <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>
  }
  if (!summary) return <p className="text-sm text-command-500">Loading report…</p>

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-bold">Reports & Analytics</h2>
          <p className="text-sm text-command-600">Post-event summary metrics and exports.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="btn-secondary"
            disabled={Boolean(exporting)}
            onClick={() => downloadExport('/reports/export.csv', 'disaster_report.csv', 'csv')}
          >
            {exporting === 'csv' ? 'Exporting…' : 'Export CSV'}
          </button>
          <button
            type="button"
            className="btn-primary"
            disabled={Boolean(exporting)}
            onClick={() => downloadExport('/reports/export.pdf', 'disaster_report.pdf', 'pdf')}
          >
            {exporting === 'pdf' ? 'Exporting…' : 'Export PDF'}
          </button>
        </div>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ['Affected Population', summary.total_affected_population],
          ['Resources Requested', summary.total_resources_requested],
          ['Resources Allocated', summary.total_resources_allocated],
          ['Total Shortages', summary.total_shortages],
          ['Zone Coverage', `${summary.zone_coverage_pct}%`],
          ['Field Missions', summary.field_missions],
          ['Missions Completed', summary.missions_completed],
          ['Resource Utilization', `${summary.resource_utilization_pct}%`],
        ].map(([label, value]) => (
          <div key={label} className="card">
            <p className="text-xs uppercase text-command-500">{label}</p>
            <p className="mt-2 text-2xl font-semibold">{typeof value === 'number' ? formatNumber(value) : value}</p>
          </div>
        ))}
      </div>

      <div className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b text-xs uppercase text-command-500">
            <tr>
              <th className="py-2 text-left">Disaster</th>
              <th className="py-2 text-left">Severity</th>
              <th className="py-2 text-left">Status</th>
              <th className="py-2 text-left">Affected</th>
            </tr>
          </thead>
          <tbody>
            {summary.disasters.map((d) => (
              <tr key={d.id} className="border-b border-command-100">
                <td className="py-2 font-medium">{d.title}</td>
                <td className="py-2"><StatusBadge value={d.severity} /></td>
                <td className="py-2"><StatusBadge value={d.status} /></td>
                <td className="py-2">{formatNumber(d.affected_population)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
