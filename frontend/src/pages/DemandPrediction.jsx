import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts'
import api from '../services/api'
import EndToEndPipeline from '../components/EndToEndPipeline'
import { formatNumber, formatPercent } from '../utils/format'
import { opsLink, readOpsQuery } from '../utils/opsLinks'

export default function DemandPrediction() {
  const [searchParams] = useSearchParams()
  const q = readOpsQuery(searchParams)

  const [disasters, setDisasters] = useState([])
  const [disasterId, setDisasterId] = useState(q.disasterId || '')
  const [zoneId, setZoneId] = useState(q.zoneId || '')
  const [result, setResult] = useState(null)
  const [metrics, setMetrics] = useState([])
  const [best, setBest] = useState({})
  const [status, setStatus] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [updateReason, setUpdateReason] = useState('Updated field damage assessment')

  const selectedDisaster = disasters.find((d) => String(d.id) === String(disasterId))
  const zones = selectedDisaster?.zones || []
  const selectedZone = zones.find((z) => String(z.id) === String(zoneId))

  useEffect(() => {
    Promise.all([
      api.get('/disasters'),
      api.get('/predict/status'),
      api.get('/predict/metrics').catch(() => ({ data: { results: [], best_models: {} } })),
    ])
      .then(([d, s, m]) => {
        setDisasters(d.data)
        const did = q.disasterId || (d.data[0] ? String(d.data[0].id) : '')
        const disaster = d.data.find((x) => String(x.id) === String(did)) || d.data[0]
        setDisasterId(disaster ? String(disaster.id) : '')
        const zid =
          q.zoneId ||
          (disaster?.zones?.[0] ? String(disaster.zones[0].id) : '')
        setZoneId(zid)
        setStatus(s.data)
        setMetrics(m.data.results || [])
        setBest(m.data.best_models || {})
      })
      .catch((err) => setError(err.message))
  }, [])

  function zonePayload(zone) {
    return {
      latitude: zone.latitude,
      longitude: zone.longitude,
      population: zone.population,
      population_density: zone.population_density,
      vulnerability_score: zone.vulnerability_score,
      severity_score: zone.severity === 'critical' ? 0.95 : zone.severity === 'high' ? 0.8 : zone.priority === 'critical' ? 0.9 : 0.55,
      building_damage_pct: zone.building_damage_pct,
      road_damage_pct: zone.road_damage_pct,
      rainfall: zone.rainfall,
      humidity: zone.humidity,
      accessibility_score: zone.accessibility_score,
      elderly_pct: 12,
      children_pct: 22,
      medical_dependency_pct: 8,
      medically_dependent_pct: 8,
      disaster_type: selectedDisaster?.disaster_type || 'Flood',
      subtype: selectedDisaster?.subtype || 'River Flood',
      disaster_subtype: selectedDisaster?.subtype || 'River Flood',
      disaster_id: zone.disaster_id,
      zone_id: zone.id,
    }
  }

  async function predict() {
    if (!selectedZone) return
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/predict/demand', zonePayload(selectedZone))
      setResult(data)
      const refreshed = await api.get('/disasters')
      setDisasters(refreshed.data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function updatePredict() {
    if (!selectedZone) return
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/predict/demand/update', {
        ...zonePayload(selectedZone),
        building_damage_pct: Math.min(100, selectedZone.building_damage_pct + 10),
        reason: updateReason,
      })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const bestRows = Object.entries(best).map(([target, info]) => ({
    target,
    model: info.model,
    r2: info.test_r2,
    accuracy: info.accuracy_r2_pct,
  }))

  const metricByModel = {}
  metrics.forEach((row) => {
    if (!metricByModel[row.model]) metricByModel[row.model] = { model: row.model, r2: 0, n: 0, mae: 0, rmse: 0, accuracy: 0 }
    metricByModel[row.model].r2 += row.test_r2
    metricByModel[row.model].accuracy += row.accuracy_r2_pct
    metricByModel[row.model].mae += row.mae
    metricByModel[row.model].rmse += row.rmse
    metricByModel[row.model].n += 1
  })
  const perfTable = Object.values(metricByModel).map((m) => ({
    model: m.model,
    r2: (m.r2 / m.n).toFixed(4),
    accuracy: (m.accuracy / m.n).toFixed(2),
    mae: (m.mae / m.n).toFixed(1),
    rmse: (m.rmse / m.n).toFixed(1),
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">AI Demand Prediction</h2>
        <p className="text-sm text-command-600">
          Step 1 of the relief pipeline: predict zone demand, then allocate stock.
          {status && !status.ready && (
            <span className="ml-2 text-red-700">Models not loaded — run ml/train_models.py</span>
          )}
        </p>
      </div>

      <EndToEndPipeline activeId="demand" disasterId={disasterId} zoneId={zoneId} />

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      <div className="card grid gap-3 md:grid-cols-4">
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Disaster</label>
          <select className="w-full rounded border px-3 py-2 text-sm" value={disasterId} onChange={(e) => { setDisasterId(e.target.value); const d = disasters.find((x) => String(x.id) === e.target.value); setZoneId(d?.zones?.[0]?.id || '') }}>
            {disasters.map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Zone</label>
          <select className="w-full rounded border px-3 py-2 text-sm" value={zoneId} onChange={(e) => setZoneId(e.target.value)}>
            {zones.map((z) => <option key={z.id} value={z.id}>{z.name}</option>)}
          </select>
        </div>
        <div className="flex items-end gap-2 md:col-span-2">
          <button type="button" className="btn-primary" disabled={loading || !selectedZone} onClick={predict}>
            {loading ? 'Predicting…' : 'Predict Demand'}
          </button>
          <button type="button" className="btn-secondary" disabled={loading || !selectedZone} onClick={updatePredict}>
            Recalculate (Update)
          </button>
        </div>
      </div>

      {result && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              ['Food Demand', result.food_demand, 'packets'],
              ['Water Demand', result.water_demand_litres, 'litres'],
              ['Medical Kits', result.medical_kit_demand, 'kits'],
              ['Shelter Demand', result.shelter_demand, 'beds'],
            ].map(([label, value, unit]) => (
              <div key={label} className="card">
                <p className="text-xs uppercase text-command-500">{label}</p>
                <p className="mt-2 text-3xl font-semibold">{formatNumber(value)}</p>
                <p className="text-xs text-command-500">{unit}</p>
              </div>
            ))}
          </div>

          <div className="card grid gap-4 md:grid-cols-3 text-sm">
            <div>
              <h3 className="font-semibold">Base Demand</h3>
              <ul className="mt-2 space-y-1 text-command-700">
                {Object.entries(result.base_demand || {}).map(([k, v]) => (
                  <li key={k}>{k}: {formatNumber(v)}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold">+ Vulnerability Adjustment</h3>
              <p className="mt-2 text-2xl font-semibold text-amber-800">{formatPercent(result.vulnerability_adjustment * 100)}</p>
              <p className="text-xs text-command-500">{result.formula}</p>
            </div>
            <div>
              <h3 className="font-semibold">= Final Demand</h3>
              <p className="mt-2 text-command-700">Models: {Object.values(result.models_used || {}).join(', ')}</p>
              {result.percentage_change && (
                <div className="mt-2 rounded bg-command-50 p-2 text-xs">
                  <p className="font-semibold">Update vs previous</p>
                  {Object.entries(result.percentage_change).map(([k, v]) => (
                    <p key={k}>{k}: {v > 0 ? '+' : ''}{v}%</p>
                  ))}
                  <p className="mt-1">Reason: {result.reason || updateReason}</p>
                </div>
              )}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Link
              className="btn-primary"
              to={opsLink('/allocation', { disasterId, zoneId })}
            >
              Next: Resource Allocation →
            </Link>
            <Link className="btn-secondary" to="/resources">
              Check Stock →
            </Link>
          </div>
        </>
      )}

      <div className="card">
        <h3 className="mb-2 font-semibold">Model Performance (averaged across targets)</h3>
        <p className="mb-3 text-xs text-command-500">
          Accuracy column is <strong>R²-based Accuracy (%)</strong> = Test R² × 100 — not classification accuracy.
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="border-b text-xs uppercase text-command-500">
              <tr>
                <th className="py-2 text-left">Model</th>
                <th className="py-2 text-left">R²</th>
                <th className="py-2 text-left">R²-based Accuracy %</th>
                <th className="py-2 text-left">MAE</th>
                <th className="py-2 text-left">RMSE</th>
              </tr>
            </thead>
            <tbody>
              {perfTable.map((row) => {
                const isBest = bestRows.some((b) => b.model === row.model)
                return (
                  <tr key={row.model} className={`border-b ${isBest ? 'bg-green-50' : ''}`}>
                    <td className="py-2 font-medium">{row.model}{isBest ? ' ★' : ''}</td>
                    <td className="py-2">{row.r2}</td>
                    <td className="py-2">{row.accuracy}</td>
                    <td className="py-2">{row.mae}</td>
                    <td className="py-2">{row.rmse}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {bestRows.length > 0 && (
        <div className="card h-72">
          <h3 className="mb-2 font-semibold">Best Model per Target (Test R²)</h3>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={bestRows}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="target" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="accuracy" name="R²-based Accuracy %" fill="#334e68" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
