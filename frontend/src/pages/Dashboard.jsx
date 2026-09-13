import { useEffect, useState } from 'react'
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
import DisasterMap from '../components/DisasterMap'
import StatusBadge from '../components/StatusBadge'
import { formatNumber } from '../utils/format'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [selectedZone, setSelectedZone] = useState(null)

  useEffect(() => {
    setLoading(true)
    api
      .get('/dashboard/summary')
      .then(({ data: d }) => setData(d))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p className="text-sm text-command-500">Loading command dashboard…</p>
  if (error) return <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>
  if (!data) return null

  const cards = [
    ['Active Disasters', data.cards.active_disasters],
    ['Affected Population', data.cards.affected_population],
    ['Available Resources', data.cards.available_resources],
    ['Predicted Demand', data.cards.predicted_demand],
    ['Resource Shortage', data.cards.resource_shortage],
    ['Field Teams Active', data.cards.field_teams_active],
  ]

  const demandChart = data.zones.map((z) => ({
    name: z.name.replace(/^Zone\s*/, '').slice(0, 14),
    food: z.food_demand || 0,
    water: (z.water_demand_litres || 0) / 100,
    medical: z.medical_kit_demand || 0,
    shelter: z.shelter_demand || 0,
  }))

  const resourceChart = data.resources.slice(0, 8).map((r) => ({
    name: r.name.slice(0, 12),
    available: r.quantity_available,
    reserved: r.quantity_reserved,
    deployed: r.quantity_deployed,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold text-command-900">Operations Dashboard</h2>
        <p className="mt-1 text-sm text-command-600">
          Command overview for monitoring, demand, allocation, and field coordination.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {cards.map(([label, value]) => (
          <div key={label} className="card">
            <p className="text-xs font-medium uppercase tracking-wide text-command-500">{label}</p>
            <p className="mt-2 text-2xl font-semibold text-command-900">{formatNumber(value)}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="card lg:col-span-3">
          <h3 className="mb-3 font-semibold">Interactive Disaster Map</h3>
          <DisasterMap
            disasters={data.disasters}
            zones={data.zones}
            teams={data.teams}
            onZoneClick={setSelectedZone}
            height="360px"
          />
          {selectedZone && (
            <div className="mt-3 rounded border border-command-200 bg-command-50 p-3 text-sm">
              <p className="font-semibold">{selectedZone.name}</p>
              <p>Population {formatNumber(selectedZone.population)} · Priority {selectedZone.priority}</p>
              <p>
                Food {formatNumber(selectedZone.food_demand)} · Water {formatNumber(selectedZone.water_demand_litres)} ·
                Medical {formatNumber(selectedZone.medical_kit_demand)} · Shelter {formatNumber(selectedZone.shelter_demand)}
              </p>
            </div>
          )}
        </div>
        <div className="card lg:col-span-2">
          <h3 className="mb-3 font-semibold">Critical Zones</h3>
          <div className="space-y-2">
            {data.critical_zones.map((z) => (
              <div key={z.id} className="flex items-center justify-between rounded border border-command-100 px-3 py-2 text-sm">
                <div>
                  <p className="font-medium">{z.name}</p>
                  <p className="text-xs text-command-500">Pop {formatNumber(z.population)}</p>
                </div>
                <StatusBadge value={z.priority} />
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card h-80">
          <h3 className="mb-3 font-semibold">Demand by Zone</h3>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={demandChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="food" fill="#334e68" name="Food" />
              <Bar dataKey="medical" fill="#b91c1c" name="Medical" />
              <Bar dataKey="shelter" fill="#0f766e" name="Shelter" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card h-80">
          <h3 className="mb-3 font-semibold">Resource Availability</h3>
          <ResponsiveContainer width="100%" height="85%">
            <BarChart data={resourceChart}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="available" fill="#15803d" />
              <Bar dataKey="reserved" fill="#a16207" />
              <Bar dataKey="deployed" fill="#1d4ed8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="mb-3 font-semibold">Active / Recent Missions</h3>
        {data.recent_missions.length === 0 ? (
          <p className="text-sm text-command-500">No missions yet. Create them under Missions.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b text-xs uppercase text-command-500">
                <tr>
                  <th className="py-2 text-left">ID</th>
                  <th className="py-2 text-left">Title</th>
                  <th className="py-2 text-left">Priority</th>
                  <th className="py-2 text-left">Status</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_missions.map((m) => (
                  <tr key={m.id} className="border-b border-command-100">
                    <td className="py-2">{m.id}</td>
                    <td className="py-2 font-medium">{m.title}</td>
                    <td className="py-2"><StatusBadge value={m.priority} /></td>
                    <td className="py-2"><StatusBadge value={m.status} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
