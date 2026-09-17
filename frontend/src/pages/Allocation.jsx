import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import EndToEndPipeline from '../components/EndToEndPipeline'
import { formatNumber, formatPercent } from '../utils/format'
import { opsLink, readOpsQuery } from '../utils/opsLinks'

export default function Allocation() {
  const [searchParams] = useSearchParams()
  const q = readOpsQuery(searchParams)

  const [disasters, setDisasters] = useState([])
  const [disasterId, setDisasterId] = useState(q.disasterId || '')
  const [result, setResult] = useState(null)
  const [supplies, setSupplies] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    api
      .get('/disasters')
      .then(({ data }) => {
        setDisasters(data)
        const initial = q.disasterId || (data[0] ? String(data[0].id) : '')
        setDisasterId(initial)
      })
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    if (!disasterId) return
    api
      .get(`/optimization/plan/${disasterId}`)
      .then(({ data }) => {
        if (data.allocations?.length) setResult(data)
      })
      .catch(() => {})
    api
      .get('/resources')
      .then(({ data }) => {
        const totals = { food_packets: 0, water: 0, medical_kits: 0, shelter: 0 }
        ;(data || []).forEach((r) => {
          if (r.resource_type in totals) totals[r.resource_type] += Number(r.quantity_available || 0)
        })
        setSupplies(totals)
      })
      .catch(() => {})
  }, [disasterId])

  async function run() {
    setLoading(true)
    setError('')
    setMessage('')
    try {
      const { data } = await api.post('/optimization/allocate', {
        disaster_id: Number(disasterId),
        transport_capacity: 2000000,
      })
      setResult(data)
      setMessage(data.message || 'Allocation complete')
      const refreshed = await api.get('/resources')
      const totals = { food_packets: 0, water: 0, medical_kits: 0, shelter: 0 }
      ;(refreshed.data || []).forEach((r) => {
        if (r.resource_type in totals) totals[r.resource_type] += Number(r.quantity_available || 0)
      })
      setSupplies(totals)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const firstZoneId =
    q.zoneId ||
    result?.by_zone?.[0]?.zone_id ||
    disasters.find((d) => String(d.id) === String(disasterId))?.zones?.[0]?.id ||
    ''

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Resource Allocation</h2>
        <p className="text-sm text-command-600">
          Match zone demand against depot stock. Priority and accessibility decide how scarce
          supplies are split — then reserve inventory for logistics and missions.
        </p>
      </div>

      <EndToEndPipeline activeId="allocate" disasterId={disasterId} zoneId={firstZoneId} />

      <div className="card grid gap-3 text-sm md:grid-cols-4">
        <div className="rounded border border-command-100 bg-command-50 p-3">
          <p className="text-xs font-semibold uppercase text-command-500">Inputs</p>
          <p className="mt-1 text-command-800">Zone demand (AI) + depot availability + priority</p>
        </div>
        <div className="rounded border border-teal-200 bg-teal-50 p-3 md:col-span-2">
          <p className="text-xs font-semibold uppercase text-teal-800">This step</p>
          <p className="mt-1 text-teal-950">
            Optimize allocation → save plan → move stock <strong>available → reserved</strong>
          </p>
        </div>
        <div className="rounded border border-command-100 bg-command-50 p-3">
          <p className="text-xs font-semibold uppercase text-command-500">Outputs</p>
          <p className="mt-1 text-command-800">Per-zone resource plan for routes &amp; missions</p>
        </div>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      {message && <div className="rounded-md bg-teal-50 p-3 text-sm text-teal-900">{message}</div>}

      <div className="card flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Disaster</label>
          <select
            className="rounded border px-3 py-2 text-sm"
            value={disasterId}
            onChange={(e) => {
              setDisasterId(e.target.value)
              setResult(null)
            }}
          >
            {disasters.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title}
              </option>
            ))}
          </select>
        </div>
        <button type="button" className="btn-primary" onClick={run} disabled={loading || !disasterId}>
          {loading ? 'Optimizing…' : 'Run Resource Allocation'}
        </button>
        <Link
          className="btn-secondary"
          to={opsLink('/demand', { disasterId, zoneId: firstZoneId })}
        >
          ← Back: Predict Demand
        </Link>
        <Link className="btn-secondary" to="/resources">
          Check Stock
        </Link>
      </div>

      {supplies && (
        <div className="card">
          <h3 className="mb-2 font-semibold">Current available stock (inputs)</h3>
          <div className="grid gap-3 sm:grid-cols-4 text-sm">
            {Object.entries(supplies).map(([k, v]) => (
              <div key={k} className="rounded border px-3 py-2">
                <p className="text-xs uppercase text-command-500">{k.replace('_', ' ')}</p>
                <p className="text-lg font-semibold">{formatNumber(v)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {result?.summary && (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <div className="card">
              <p className="text-xs uppercase text-command-500">Requested (demand)</p>
              <p className="text-2xl font-semibold">{formatNumber(result.summary.total_requested)}</p>
            </div>
            <div className="card">
              <p className="text-xs uppercase text-command-500">Allocated</p>
              <p className="text-2xl font-semibold">{formatNumber(result.summary.total_allocated)}</p>
            </div>
            <div className="card">
              <p className="text-xs uppercase text-command-500">Coverage</p>
              <p className="text-2xl font-semibold">
                {formatPercent(result.summary.overall_coverage_pct)}
              </p>
              <p className="text-xs text-command-500">Solver: {result.summary.solver_status}</p>
            </div>
          </div>

          {result.by_zone?.length > 0 && (
            <div className="card space-y-3">
              <h3 className="font-semibold">Allocation by zone (use for logistics &amp; missions)</h3>
              <div className="grid gap-3 md:grid-cols-2">
                {result.by_zone.map((z) => (
                  <div key={z.zone_id} className="rounded border p-3 text-sm">
                    <div className="mb-2 flex items-center justify-between gap-2">
                      <span className="font-medium">{z.zone}</span>
                      <StatusBadge value={z.priority} />
                    </div>
                    <ul className="space-y-1 text-command-700">
                      {Object.entries(z.resources || {}).map(([rtype, qty]) => (
                        <li key={rtype}>
                          {rtype}: <strong>{formatNumber(qty)}</strong>
                        </li>
                      ))}
                    </ul>
                    <div className="mt-3 flex flex-wrap gap-2">
                      <Link
                        className="btn-primary py-1 text-xs"
                        to={opsLink('/logistics', { disasterId, zoneId: z.zone_id })}
                      >
                        Plan route →
                      </Link>
                      <Link
                        className="btn-secondary py-1 text-xs"
                        to={opsLink('/missions', { disasterId, zoneId: z.zone_id })}
                      >
                        Assign mission →
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="card overflow-x-auto">
            <h3 className="mb-2 font-semibold">Full allocation detail</h3>
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
                {(result.allocations || []).map((row, i) => (
                  <tr key={`${row.zone_id}-${row.resource}-${i}`} className="border-b border-command-100">
                    <td className="py-2">{row.zone}</td>
                    <td className="py-2">{row.resource}</td>
                    <td className="py-2">{formatNumber(row.requested_quantity)}</td>
                    <td className="py-2">{formatNumber(row.allocated_quantity)}</td>
                    <td className="py-2">{formatNumber(row.shortage)}</td>
                    <td className="py-2">{formatPercent(row.coverage_percentage)}</td>
                    <td className="py-2">
                      <StatusBadge value={row.priority} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link
              className="btn-primary"
              to={opsLink('/logistics', { disasterId, zoneId: firstZoneId })}
            >
              Next: Logistics &amp; Routing →
            </Link>
            <Link
              className="btn-secondary"
              to={opsLink('/missions', { disasterId, zoneId: firstZoneId })}
            >
              Next: Assign Mission →
            </Link>
          </div>
        </>
      )}

      {!result && !loading && (
        <div className="card text-sm text-command-600">
          No plan loaded. Run allocation after predicting demand and checking depot stock.
        </div>
      )}
    </div>
  )
}
