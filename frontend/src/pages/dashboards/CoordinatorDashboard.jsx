import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from 'recharts'
import api from '../../services/api'
import DisasterMap from '../../components/DisasterMap'
import StatusBadge from '../../components/StatusBadge'
import OpsWorkflow from '../../components/OpsWorkflow'
import { formatNumber } from '../../utils/format'
import { useAuth } from '../../hooks/useAuth'

export default function CoordinatorDashboard() {
  const { user } = useAuth()
  const [data, setData] = useState(null)
  const [missions, setMissions] = useState([])
  const [error, setError] = useState('')
  const [selectedZone, setSelectedZone] = useState(null)

  useEffect(() => {
    Promise.all([api.get('/dashboard/summary'), api.get('/missions')])
      .then(([dash, mis]) => {
        setData(dash.data)
        setMissions(mis.data.slice(0, 8))
      })
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>
  if (!data) return <p className="text-sm text-command-500">Loading operations desk…</p>

  const demandChart = data.zones.map((z) => ({
    name: z.name.replace(/^Zone\s*/, '').slice(0, 12),
    food: z.food_demand || 0,
    medical: z.medical_kit_demand || 0,
    shelter: z.shelter_demand || 0,
  }))

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-orange-700">Relief Coordinator</p>
        <h2 className="font-display text-2xl font-bold">Main Disaster Operations Dashboard</h2>
        <p className="mt-1 text-sm text-command-600">
          {user?.full_name} — full response pipeline from disaster data through dynamic AI updates.
        </p>
      </div>

      <div className="card">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-semibold">End-to-end operations workflow</h3>
          <Link to="/workflow" className="text-xs font-medium text-command-700 underline">Open full workflow board</Link>
        </div>
        <OpsWorkflow compact />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        {[
          ['Active Disasters', data.cards.active_disasters],
          ['Affected Population', data.cards.affected_population],
          ['Available Resources', data.cards.available_resources],
          ['Predicted Demand', data.cards.predicted_demand],
          ['Resource Shortage', data.cards.resource_shortage],
          ['Teams Active', data.cards.field_teams_active],
        ].map(([label, value]) => (
          <div key={label} className="card">
            <p className="text-xs uppercase text-command-500">{label}</p>
            <p className="mt-2 text-2xl font-semibold">{formatNumber(value)}</p>
          </div>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        <div className="card lg:col-span-3">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="font-semibold">Geospatial Assessment & Zones</h3>
            <Link to="/disasters" className="text-xs underline">Manage zones / priority →</Link>
          </div>
          <DisasterMap
            disasters={data.disasters}
            zones={data.zones}
            teams={data.teams}
            onZoneClick={setSelectedZone}
            height="360px"
          />
          {selectedZone && (
            <div className="mt-3 rounded border bg-command-50 p-3 text-sm space-y-2">
              <p className="font-semibold">{selectedZone.name}</p>
              <p>Priority <StatusBadge value={selectedZone.priority} /> · Pop {formatNumber(selectedZone.population)}</p>
              <p className="text-xs text-command-600">
                Food {formatNumber(selectedZone.food_demand)} · Water {formatNumber(selectedZone.water_demand_litres)} ·
                Medical {formatNumber(selectedZone.medical_kit_demand)} · Shelter {formatNumber(selectedZone.shelter_demand)}
              </p>
              <div className="flex flex-wrap gap-2">
                <Link
                  className="btn-primary py-1 text-xs"
                  to={`/demand?disaster_id=${selectedZone.disaster_id || ''}&zone_id=${selectedZone.id}`}
                >
                  1. Predict Demand
                </Link>
                <Link
                  className="btn-secondary py-1 text-xs"
                  to={`/allocation?disaster_id=${selectedZone.disaster_id || ''}&zone_id=${selectedZone.id}`}
                >
                  2. Allocate Resources
                </Link>
                <Link
                  className="btn-secondary py-1 text-xs"
                  to={`/logistics?disaster_id=${selectedZone.disaster_id || ''}&zone_id=${selectedZone.id}`}
                >
                  3. Plan Route
                </Link>
                <Link
                  className="btn-secondary py-1 text-xs"
                  to={`/missions?disaster_id=${selectedZone.disaster_id || ''}&zone_id=${selectedZone.id}`}
                >
                  4. Assign Mission
                </Link>
              </div>
            </div>
          )}
        </div>
        <div className="card lg:col-span-2 space-y-3">
          <h3 className="font-semibold">Critical / High Zones</h3>
          {data.critical_zones.map((z) => (
            <button
              key={z.id}
              type="button"
              className="flex w-full items-center justify-between rounded border px-3 py-2 text-left text-sm"
              onClick={() => setSelectedZone(data.zones.find((x) => x.id === z.id) || z)}
            >
              <span>{z.name}</span>
              <StatusBadge value={z.priority} />
            </button>
          ))}
          <h3 className="font-semibold pt-2">Missions (Field Response)</h3>
          {missions.length === 0 ? (
            <p className="text-sm text-command-500">No missions. <Link to="/missions" className="underline">Assign one</Link></p>
          ) : (
            missions.map((m) => (
              <div key={m.id} className="rounded border px-3 py-2 text-sm">
                <div className="flex justify-between gap-2">
                  <span className="font-medium">{m.title}</span>
                  <StatusBadge value={m.status} />
                </div>
              </div>
            ))
          )}
          <div className="rounded border border-teal-200 bg-teal-50 p-3 text-xs text-teal-900 space-y-2">
            <p className="font-semibold">After field reports</p>
            <p>Dynamic AI Update: recalculate demand, then reallocate if needed.</p>
            <div className="flex flex-wrap gap-2">
              <Link to="/demand" className="btn-primary py-1 text-xs">1. Recalculate Demand</Link>
              <Link to="/allocation" className="btn-secondary py-1 text-xs">2. Reallocate Resources</Link>
              <Link to="/logistics" className="btn-secondary py-1 text-xs">3. Re-plan Routes</Link>
            </div>
          </div>
        </div>
      </div>

      <div className="card h-72">
        <h3 className="mb-2 font-semibold">AI Demand Snapshot by Zone</h3>
        <ResponsiveContainer width="100%" height="85%">
          <BarChart data={demandChart}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" tick={{ fontSize: 10 }} />
            <YAxis tick={{ fontSize: 10 }} />
            <Tooltip />
            <Legend />
            <Bar dataKey="food" fill="#334e68" name="Food" />
            <Bar dataKey="medical" fill="#b91c1c" name="Medical" />
            <Bar dataKey="shelter" fill="#0f766e" name="Shelter" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
