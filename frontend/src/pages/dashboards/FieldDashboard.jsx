import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../../services/api'
import StatusBadge from '../../components/StatusBadge'
import DisasterMap from '../../components/DisasterMap'
import OpsWorkflow from '../../components/OpsWorkflow'
import { formatNumber } from '../../utils/format'
import { useAuth } from '../../hooks/useAuth'

export default function FieldDashboard() {
  const { user } = useAuth()
  const [missions, setMissions] = useState([])
  const [selectedId, setSelectedId] = useState(null)
  const [detail, setDetail] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(false)
  const [report, setReport] = useState({
    population_affected: '',
    building_damage_pct: '',
    road_damage_pct: '',
    accessibility_score: '0.7',
    severity: 'high',
    notes: '',
    evidence_note: '',
  })

  async function loadMissions() {
    const { data } = await api.get('/missions')
    setMissions(data)
    if (!selectedId && data[0]) setSelectedId(data[0].id)
  }

  async function loadDetail(id) {
    if (!id) return
    const { data } = await api.get(`/missions/${id}/detail`)
    setDetail(data)
    if (data.zone) {
      setReport((r) => ({
        ...r,
        population_affected: data.zone.population || '',
        building_damage_pct: data.zone.building_damage_pct || '',
        road_damage_pct: data.zone.road_damage_pct || '',
      }))
    }
  }

  useEffect(() => {
    setLoading(true)
    loadMissions()
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    if (selectedId) {
      loadDetail(selectedId).catch((err) => setError(err.message))
    }
  }, [selectedId])

  const active = useMemo(
    () => missions.filter((m) => !['completed', 'cancelled'].includes(m.status)),
    [missions],
  )
  const criticalAlerts = useMemo(
    () => active.filter((m) => ['critical', 'high'].includes(m.priority)),
    [active],
  )

  const routeLine = useMemo(() => {
    const coords = detail?.route?.route_geometry?.coordinates
    if (!coords) return null
    return coords.map(([lon, lat]) => [lat, lon])
  }, [detail])

  async function setStatus(status) {
    if (!selectedId) return
    setUpdating(true)
    setError('')
    try {
      await api.patch(`/missions/${selectedId}/status`, { status })
      await loadMissions()
      await loadDetail(selectedId)
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdating(false)
    }
  }

  async function submitReport(e) {
    e.preventDefault()
    if (!detail?.zone?.id) return
    setUpdating(true)
    setError('')
    try {
      await api.post('/field-reports', {
        zone_id: detail.zone.id,
        mission_id: selectedId,
        population_affected: report.population_affected === '' ? null : Number(report.population_affected),
        building_damage_pct: report.building_damage_pct === '' ? null : Number(report.building_damage_pct),
        road_damage_pct: report.road_damage_pct === '' ? null : Number(report.road_damage_pct),
        accessibility_score: Number(report.accessibility_score),
        severity: report.severity,
        notes: report.notes,
        evidence_note: report.evidence_note || null,
      })
      setReport((r) => ({ ...r, notes: '', evidence_note: '' }))
      await loadDetail(selectedId)
      alert('Field report submitted. Coordinators can now run Dynamic AI Update (recalculate demand).')
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <p className="text-sm text-command-500">Loading field dashboard…</p>

  return (
    <div className="mx-auto max-w-5xl space-y-4 pb-24 md:pb-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-teal-700">Field Team</p>
        <h2 className="font-display text-xl font-bold md:text-2xl">My Field Operations</h2>
        <p className="text-sm text-command-600">
          {user?.full_name} — your segment: Mission → Navigate → Deliver → Status → Field Report → feeds Dynamic AI Update
        </p>
      </div>

      <div className="card">
        <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-command-500">
          Where you sit in the full pipeline
        </p>
        <OpsWorkflow
          compact
          showHeader={false}
          highlightIds={['mission', 'field', 'report', 'logistics', 'availability', 'update']}
        />
        <p className="mt-2 text-xs text-teal-800">
          Your field report lets coordinators recalculate demand and reallocate resources.
        </p>
      </div>

      {criticalAlerts.length > 0 && (
        <div className="rounded-md border border-red-300 bg-red-50 p-3 text-sm text-red-900">
          <p className="font-semibold">Emergency / Priority notification</p>
          <p>{criticalAlerts.length} high/critical mission(s) need attention.</p>
        </div>
      )}

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="card py-3"><p className="text-xs uppercase text-command-500">Active</p><p className="text-2xl font-semibold">{active.length}</p></div>
        <div className="card py-3"><p className="text-xs uppercase text-command-500">Completed</p><p className="text-2xl font-semibold">{missions.filter((m) => m.status === 'completed').length}</p></div>
        <div className="card py-3"><p className="text-xs uppercase text-command-500">Priority Alerts</p><p className="text-2xl font-semibold">{criticalAlerts.length}</p></div>
      </div>

      {/* Mission list - touch friendly */}
      <div className="card">
        <h3 className="mb-2 font-semibold">My Assigned Missions</h3>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {missions.map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setSelectedId(m.id)}
              className={`min-w-[9.5rem] rounded-md border px-3 py-3 text-left text-sm ${
                selectedId === m.id ? 'border-teal-600 bg-teal-50' : 'border-command-200'
              }`}
            >
              <p className="font-medium line-clamp-2">{m.title}</p>
              <div className="mt-2 flex flex-wrap gap-1">
                <StatusBadge value={m.priority} />
                <StatusBadge value={m.status} />
              </div>
            </button>
          ))}
        </div>
      </div>

      {detail && (
        <>
          <div className="card space-y-2">
            <h3 className="font-semibold">Mission Details #{detail.mission.id}</h3>
            <p className="text-sm">{detail.mission.instructions || 'Follow assigned relief SOP.'}</p>
            <div className="grid gap-2 text-sm sm:grid-cols-2">
              <p>Disaster: <strong>{detail.disaster?.title}</strong></p>
              <p>Zone: <strong>{detail.zone?.name}</strong></p>
              <p>Team: <strong>{detail.team?.name}</strong> ({detail.team?.leader_name})</p>
              <p>Priority: <StatusBadge value={detail.mission.priority} /></p>
            </div>
            {detail.alerts?.map((a, i) => (
              <p key={i} className={`text-xs rounded px-2 py-1 ${a.level === 'critical' ? 'bg-red-100 text-red-800' : 'bg-command-100'}`}>
                {a.message}
              </p>
            ))}
          </div>

          <div className="card space-y-2">
            <div className="flex items-center justify-between gap-2">
              <h3 className="font-semibold">Navigate / Route</h3>
              {detail.route && (
                <a
                  className="btn-primary py-1.5 text-xs"
                  href={`https://www.openstreetmap.org/directions?from=${detail.route.depot.latitude}%2C${detail.route.depot.longitude}&to=${detail.zone.latitude}%2C${detail.zone.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Open Navigation
                </a>
              )}
            </div>
            {detail.route ? (
              <p className="text-sm text-command-600">
                {detail.route.demo_label} · {detail.route.distance_km} km · ETA {detail.route.estimated_time_hours} h
              </p>
            ) : (
              <p className="text-sm text-command-500">No route available.</p>
            )}
            {detail.zone && (
              <DisasterMap
                zones={[detail.zone]}
                depots={detail.route?.depot ? [detail.route.depot] : []}
                routeLine={routeLine}
                height="220px"
              />
            )}
          </div>

          <div className="card">
            <h3 className="mb-2 font-semibold">Resource Manifest (Deliver)</h3>
            {Object.keys(detail.resource_manifest || {}).length === 0 ? (
              <p className="text-sm text-command-500">No resources listed on this mission card.</p>
            ) : (
              <ul className="space-y-1 text-sm">
                {Object.entries(detail.resource_manifest).map(([k, v]) => (
                  <li key={k} className="flex justify-between border-b py-1">
                    <span>{k}</span>
                    <strong>{formatNumber(v)}</strong>
                  </li>
                ))}
              </ul>
            )}
            <Link to="/resources" className="mt-2 inline-block text-xs underline">Full resource list</Link>
          </div>

          <div className="card">
            <h3 className="mb-3 font-semibold">Update Mission Status</h3>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
              <button type="button" disabled={updating} className="btn-secondary min-h-12" onClick={() => setStatus('in_progress')}>
                En Route / On Site
              </button>
              <button type="button" disabled={updating} className="btn-primary min-h-12 bg-teal-700 hover:bg-teal-600" onClick={() => setStatus('completed')}>
                Mark Completed
              </button>
              <button type="button" disabled={updating} className="btn-secondary min-h-12" onClick={() => setStatus('cancelled')}>
                Cannot Complete
              </button>
            </div>
          </div>

          <form onSubmit={submitReport} className="card space-y-3">
            <h3 className="font-semibold">Submit Field Report</h3>
            <p className="text-xs text-command-500">
              Updates damage/population — feeds Dynamic AI Update for coordinators.
            </p>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="text-xs uppercase text-command-500">Affected population</label>
                <input type="number" className="mt-1 w-full rounded border px-3 py-3 text-sm" value={report.population_affected} onChange={(e) => setReport({ ...report, population_affected: e.target.value })} />
              </div>
              <div>
                <label className="text-xs uppercase text-command-500">Building damage %</label>
                <input type="number" className="mt-1 w-full rounded border px-3 py-3 text-sm" value={report.building_damage_pct} onChange={(e) => setReport({ ...report, building_damage_pct: e.target.value })} />
              </div>
              <div>
                <label className="text-xs uppercase text-command-500">Road damage %</label>
                <input type="number" className="mt-1 w-full rounded border px-3 py-3 text-sm" value={report.road_damage_pct} onChange={(e) => setReport({ ...report, road_damage_pct: e.target.value })} />
              </div>
              <div>
                <label className="text-xs uppercase text-command-500">Severity</label>
                <select className="mt-1 w-full rounded border px-3 py-3 text-sm" value={report.severity} onChange={(e) => setReport({ ...report, severity: e.target.value })}>
                  {['low', 'medium', 'high', 'critical'].map((s) => <option key={s} value={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <textarea className="w-full rounded border px-3 py-3 text-sm" rows={3} placeholder="Field notes" value={report.notes} onChange={(e) => setReport({ ...report, notes: e.target.value })} />
            <input className="w-full rounded border px-3 py-3 text-sm" placeholder="Evidence note / photo reference (optional)" value={report.evidence_note} onChange={(e) => setReport({ ...report, evidence_note: e.target.value })} />
            <button type="submit" disabled={updating} className="btn-primary w-full min-h-12">
              {updating ? 'Submitting…' : 'Submit Field Report'}
            </button>
          </form>
        </>
      )}
    </div>
  )
}
