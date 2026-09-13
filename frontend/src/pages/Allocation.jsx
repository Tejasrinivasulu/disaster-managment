import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import { formatNumber, formatPercent } from '../utils/format'

export default function Allocation() {
  const [disasters, setDisasters] = useState([])
  const [disasterId, setDisasterId] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.get('/disasters').then(({ data }) => {
      setDisasters(data)
      if (data[0]) setDisasterId(data[0].id)
    }).catch((err) => setError(err.message))
  }, [])

  async function run() {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/optimization/allocate', {
        disaster_id: Number(disasterId),
        transport_capacity: 2000000,
      })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Resource Allocation Optimization</h2>
        <p className="text-sm text-command-600">OR-Tools linear program maximizing coverage for high-priority zones.</p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      <div className="card flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Disaster</label>
          <select className="rounded border px-3 py-2 text-sm" value={disasterId} onChange={(e) => setDisasterId(e.target.value)}>
            {disasters.map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
          </select>
        </div>
        <button type="button" className="btn-primary" onClick={run} disabled={loading}>
          {loading ? 'Optimizing…' : 'Run Allocation'}
        </button>
      </div>
      {result && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="card"><p className="text-xs uppercase text-command-500">Requested</p><p className="text-2xl font-semibold">{formatNumber(result.summary.total_requested)}</p></div>
            <div className="card"><p className="text-xs uppercase text-command-500">Allocated</p><p className="text-2xl font-semibold">{formatNumber(result.summary.total_allocated)}</p></div>
            <div className="card"><p className="text-xs uppercase text-command-500">Coverage</p><p className="text-2xl font-semibold">{formatPercent(result.summary.overall_coverage_pct)}</p></div>
          </div>
          <div className="card overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b text-xs uppercase text-command-500">
                <tr>
                  <th className="py-2 text-left">Zone</th>
                  <th className="py-2 text-left">Resource</th>
                  <th className="py-2 text-left">Requested</th>
                  <th className="py-2 text-left">Allocated</th>
                  <th className="py-2 text-left">Shortage</th>
                  <th className="py-2 text-left">Coverage</th>
                  <th className="py-2 text-left">Priority</th>
                </tr>
              </thead>
              <tbody>
                {result.allocations.map((row, i) => (
                  <tr key={`${row.zone_id}-${row.resource}-${i}`} className="border-b border-command-100">
                    <td className="py-2">{row.zone}</td>
                    <td className="py-2">{row.resource}</td>
                    <td className="py-2">{formatNumber(row.requested_quantity)}</td>
                    <td className="py-2">{formatNumber(row.allocated_quantity)}</td>
                    <td className="py-2">{formatNumber(row.shortage)}</td>
                    <td className="py-2">{formatPercent(row.coverage_percentage)}</td>
                    <td className="py-2"><StatusBadge value={row.priority} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  )
}
