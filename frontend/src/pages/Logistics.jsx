import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import api from '../services/api'
import DisasterMap from '../components/DisasterMap'
import EndToEndPipeline from '../components/EndToEndPipeline'
import { formatNumber } from '../utils/format'
import { opsLink, readOpsQuery } from '../utils/opsLinks'

export default function Logistics() {
  const [searchParams] = useSearchParams()
  const q = readOpsQuery(searchParams)

  const [depots, setDepots] = useState([])
  const [disasters, setDisasters] = useState([])
  const [disasterId, setDisasterId] = useState(q.disasterId || '')
  const [depotId, setDepotId] = useState('')
  const [zoneId, setZoneId] = useState(q.zoneId || '')
  const [manifest, setManifest] = useState({ food_packets: 1000, water: 5000 })
  const [planNote, setPlanNote] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const zones = useMemo(() => {
    const d = disasters.find((x) => String(x.id) === String(disasterId))
    return d?.zones || []
  }, [disasters, disasterId])

  useEffect(() => {
    Promise.all([api.get('/resources/depots'), api.get('/disasters')])
      .then(([d, dis]) => {
        setDepots(d.data)
        setDisasters(dis.data)
        if (d.data[0]) setDepotId(d.data[0].id)
        const did = q.disasterId || (dis.data[0] ? String(dis.data[0].id) : '')
        setDisasterId(did)
        const disaster = dis.data.find((x) => String(x.id) === String(did)) || dis.data[0]
        const zid = q.zoneId || (disaster?.zones?.[0] ? String(disaster.zones[0].id) : '')
        setZoneId(zid)
      })
      .catch((err) => setError(err.message))
  }, [])

  useEffect(() => {
    if (!disasterId || !zoneId) return
    api
      .get(`/optimization/plan/${disasterId}/zone/${zoneId}`)
      .then(({ data }) => {
        if (data.resources && Object.keys(data.resources).length) {
          setManifest(data.resources)
          setPlanNote(`Loaded from allocation plan for ${data.zone || 'zone'}`)
        } else {
          setPlanNote(data.message || 'No allocation for this zone — using defaults')
        }
      })
      .catch(() => setPlanNote('Could not load allocation plan'))
  }, [disasterId, zoneId])

  async function plan() {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.post('/routes/plan', {
        depot_id: Number(depotId),
        zone_id: Number(zoneId),
        vehicle_type: 'truck',
        resources: manifest,
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
          Step 4: move allocated resources from depot → zone using the allocation plan.
        </p>
      </div>

      <EndToEndPipeline activeId="logistics" disasterId={disasterId} zoneId={zoneId} />

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      {planNote && (
        <div className="rounded-md bg-command-50 p-3 text-sm text-command-800">{planNote}</div>
      )}

      <div className="card flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs uppercase text-command-500">Disaster</label>
          <select
            className="rounded border px-3 py-2 text-sm"
            value={disasterId}
            onChange={(e) => {
              const d = disasters.find((x) => String(x.id) === e.target.value)
              setDisasterId(e.target.value)
              setZoneId(d?.zones?.[0]?.id || '')
            }}
          >
            {disasters.map((d) => (
              <option key={d.id} value={d.id}>{d.title}</option>
            ))}
          </select>
        </div>
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
        <button type="button" className="btn-primary" onClick={plan} disabled={loading || !zoneId}>
          {loading ? 'Planning…' : 'Plan Route'}
        </button>
        <Link className="btn-secondary" to={opsLink('/allocation', { disasterId, zoneId })}>
          ← Allocation
        </Link>
      </div>

      <div className="card text-sm">
        <h3 className="mb-2 font-semibold">Cargo from allocation plan</h3>
        <div className="grid gap-2 sm:grid-cols-2 md:grid-cols-4">
          {Object.entries(manifest).map(([k, v]) => (
            <div key={k} className="rounded border px-3 py-2">
              <p className="text-xs uppercase text-command-500">{k}</p>
              <p className="font-semibold">{formatNumber(v)}</p>
            </div>
          ))}
        </div>
      </div>

      {result && (
        <div className="card space-y-2 text-sm">
          <p className="badge bg-command-100 text-command-700">{result.demo_label || 'Local estimate'}</p>
          <p>Distance: <strong>{result.distance_km} km</strong></p>
          <p>ETA: <strong>{result.estimated_time_hours} hours</strong></p>
          <p>Vehicle: {result.vehicle_type} · Provider: {result.provider}</p>
          <Link className="btn-primary inline-flex" to={opsLink('/missions', { disasterId, zoneId })}>
            Next: Assign Mission →
          </Link>
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
