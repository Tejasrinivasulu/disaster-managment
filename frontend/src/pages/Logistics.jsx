import { useEffect, useMemo, useState } from 'react'
import api from '../services/api'
import DisasterMap from '../components/DisasterMap'

export default function Logistics() {
  const [depots, setDepots] = useState([])
  const [zones, setZones] = useState([])
  const [depotId, setDepotId] = useState('')
  const [zoneId, setZoneId] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    Promise.all([api.get('/resources/depots'), api.get('/zones')])
      .then(([d, z]) => {
        setDepots(d.data)
        setZones(z.data)
        if (d.data[0]) setDepotId(d.data[0].id)
        if (z.data[0]) setZoneId(z.data[0].id)
      })
      .catch((err) => setError(err.message))
  }, [])

  async function plan() {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/routes/plan', {
        depot_id: Number(depotId),
        zone_id: Number(zoneId),
        vehicle_type: 'truck',
        resources: { food_packets: 1000, water: 5000 },
      })
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const routeLine = useMemo(() => {
    if (!result?.route_geometry?.coordinates) return null
    return result.route_geometry.coordinates.map(([lon, lat]) => [lat, lon])
  }, [result])

  const selectedDepot = depots.find((d) => String(d.id) === String(depotId))
  const selectedZone = zones.find((z) => String(z.id) === String(zoneId))

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Logistics & Routing</h2>
        <p className="text-sm text-command-600">
          Depot → zone planning. Uses local distance estimates unless a live routing API is configured.
        </p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      <div className="card flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Depot</label>
          <select className="rounded border px-3 py-2 text-sm" value={depotId} onChange={(e) => setDepotId(e.target.value)}>
            {depots.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Zone</label>
          <select className="rounded border px-3 py-2 text-sm" value={zoneId} onChange={(e) => setZoneId(e.target.value)}>
            {zones.map((z) => <option key={z.id} value={z.id}>{z.name}</option>)}
          </select>
        </div>
        <button type="button" className="btn-primary" onClick={plan} disabled={loading}>
          {loading ? 'Planning…' : 'Plan Route'}
        </button>
      </div>
      {result && (
        <div className="card text-sm space-y-1">
          <p className="badge bg-command-100 text-command-700">{result.demo_label || 'Local estimate'}</p>
          <p>Distance: <strong>{result.distance_km} km</strong></p>
          <p>ETA: <strong>{result.estimated_time_hours} hours</strong></p>
          <p>Vehicle: {result.vehicle_type} · Provider: {result.provider}</p>
          <p>Realtime: {String(result.is_realtime)}</p>
        </div>
      )}
      <DisasterMap
        zones={selectedZone ? [selectedZone] : []}
        depots={selectedDepot ? [selectedDepot] : []}
        routeLine={routeLine}
        height="420px"
      />
    </div>
  )
}
