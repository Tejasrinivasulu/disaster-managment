import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts'
import api from '../services/api'
import { formatNumber, formatPercent } from '../utils/format'

const presets = {
  fast: { name: 'Scenario A — Fast Response', response_speed: 'fast', available_food: 40000, available_water: 800000, available_medical: 8000, available_shelter: 12000, transport_capacity: 500000 },
  normal: { name: 'Scenario B — Normal Response', response_speed: 'normal', available_food: 25000, available_water: 500000, available_medical: 5000, available_shelter: 8000, transport_capacity: 300000 },
  limited: { name: 'Scenario C — Limited Resources', response_speed: 'limited', available_food: 10000, available_water: 200000, available_medical: 2000, available_shelter: 3000, transport_capacity: 100000 },
}

export default function Scenarios() {
  const [disasters, setDisasters] = useState([])
  const [disasterId, setDisasterId] = useState('')
  const [results, setResults] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/disasters').then(({ data }) => {
      setDisasters(data)
      if (data[0]) setDisasterId(data[0].id)
    }).catch((err) => setError(err.message))
  }, [])

  async function runAll() {
    setError('')
    try {
      const created = []
      for (const key of Object.keys(presets)) {
        const p = presets[key]
        const { data } = await api.post('/scenarios', { ...p, disaster_id: Number(disasterId) })
        created.push(data)
      }
      setResults(created)
    } catch (err) {
      setError(err.message)
    }
  }

  const chartData = results.map((r) => ({
    name: r.name.replace('Scenario ', '').slice(0, 18),
    food_cov: r.results.coverage_percentage.food,
    water_cov: r.results.coverage_percentage.water,
    medical_cov: r.results.coverage_percentage.medical,
    shelter_cov: r.results.coverage_percentage.shelter,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Scenario Simulation</h2>
        <p className="text-sm text-command-600">Compare fast, normal, and limited-resource response scenarios.</p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      <div className="card flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Disaster</label>
          <select className="rounded border px-3 py-2 text-sm" value={disasterId} onChange={(e) => setDisasterId(e.target.value)}>
            {disasters.map((d) => <option key={d.id} value={d.id}>{d.title}</option>)}
          </select>
        </div>
        <button type="button" className="btn-primary" onClick={runAll}>Run A / B / C Comparison</button>
      </div>
      {results.length > 0 && (
        <>
          <div className="grid gap-4 md:grid-cols-3">
            {results.map((r) => (
              <div key={r.id} className="card text-sm space-y-2">
                <h3 className="font-semibold">{r.name}</h3>
                <p>Speed: {r.results.response_speed}</p>
                <p>Food shortage: {formatNumber(r.results.shortage.food)}</p>
                <p>Water shortage: {formatNumber(r.results.shortage.water)}</p>
                <p>Avg coverage: {formatPercent((r.results.coverage_percentage.food + r.results.coverage_percentage.water + r.results.coverage_percentage.medical + r.results.coverage_percentage.shelter) / 4)}</p>
              </div>
            ))}
          </div>
          <div className="card h-80">
            <h3 className="mb-2 font-semibold">Coverage Comparison</h3>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="food_cov" name="Food %" fill="#334e68" />
                <Bar dataKey="water_cov" name="Water %" fill="#0f766e" />
                <Bar dataKey="medical_cov" name="Medical %" fill="#b91c1c" />
                <Bar dataKey="shelter_cov" name="Shelter %" fill="#a16207" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  )
}
