import { useEffect, useState } from 'react'
import api from '../services/api'
import DisasterMap from '../components/DisasterMap'
import StatusBadge from '../components/StatusBadge'
import { formatNumber } from '../utils/format'

export default function ImpactMap() {
  const [data, setData] = useState(null)
  const [depots, setDepots] = useState([])
  const [selected, setSelected] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.get('/dashboard/summary'), api.get('/resources/depots')])
      .then(([dash, dep]) => {
        setData(dash.data)
        setDepots(dep.data)
      })
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>
  if (!data) return <p className="text-sm text-command-500">Loading map…</p>

  return (
    <div className="space-y-4">
      <div>
        <h2 className="font-display text-2xl font-bold">Geospatial Impact Assessment</h2>
        <p className="text-sm text-command-600">
          Interactive map of disasters, zones, depots, and teams. Click a zone for demand details.
        </p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DisasterMap
            disasters={data.disasters}
            zones={data.zones}
            teams={data.teams}
            depots={depots}
            onZoneClick={setSelected}
            height="520px"
          />
        </div>
        <div className="card">
          <h3 className="font-semibold">Zone Detail</h3>
          {!selected ? (
            <p className="mt-3 text-sm text-command-500">Select a zone on the map.</p>
          ) : (
            <dl className="mt-3 space-y-2 text-sm">
              <div><dt className="text-command-500">Name</dt><dd className="font-medium">{selected.name}</dd></div>
              <div className="flex gap-2"><StatusBadge value={selected.severity} /><StatusBadge value={selected.priority} /></div>
              <div><dt className="text-command-500">Population</dt><dd>{formatNumber(selected.population)}</dd></div>
              <div><dt className="text-command-500">Damage (buildings)</dt><dd>{selected.building_damage_pct}%</dd></div>
              <div><dt className="text-command-500">Food demand</dt><dd>{formatNumber(selected.food_demand)}</dd></div>
              <div><dt className="text-command-500">Water demand</dt><dd>{formatNumber(selected.water_demand_litres)} L</dd></div>
              <div><dt className="text-command-500">Medical demand</dt><dd>{formatNumber(selected.medical_kit_demand)}</dd></div>
              <div><dt className="text-command-500">Shelter demand</dt><dd>{formatNumber(selected.shelter_demand)}</dd></div>
              <div><dt className="text-command-500">Vulnerability</dt><dd>{selected.vulnerability_score}</dd></div>
            </dl>
          )}
        </div>
      </div>
    </div>
  )
}
