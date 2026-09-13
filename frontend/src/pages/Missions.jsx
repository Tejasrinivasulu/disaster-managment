import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import { useAuth } from '../hooks/useAuth'
import { ROLES } from '../utils/roles'

export default function Missions() {
  const { role } = useAuth()
  const canAssign = role === ROLES.ADMIN || role === ROLES.COORDINATOR
  const isField = role === ROLES.FIELD

  const [disasters, setDisasters] = useState([])
  const [teams, setTeams] = useState([])
  const [missions, setMissions] = useState([])
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const [form, setForm] = useState({
    title: '',
    instructions: '',
    disaster_id: '',
    zone_id: '',
    team_id: '',
    priority: 'high',
  })

  async function load() {
    const requests = [api.get('/missions')]
    if (canAssign) {
      requests.unshift(api.get('/disasters'), api.get('/teams'))
    }
    const results = await Promise.all(requests)
    if (canAssign) {
      const [d, t, m] = results
      setDisasters(d.data)
      setTeams(t.data)
      setMissions(m.data)
      if (!form.disaster_id && d.data[0]) {
        setForm((f) => ({
          ...f,
          disaster_id: d.data[0].id,
          zone_id: d.data[0].zones?.[0]?.id || '',
          team_id: t.data[0]?.id || '',
        }))
      }
    } else {
      setMissions(results[0].data)
    }
  }

  useEffect(() => {
    load().catch((err) => setError(err.message))
  }, [canAssign])

  const zones = disasters.find((d) => String(d.id) === String(form.disaster_id))?.zones || []

  async function create(e) {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.post('/missions', {
        ...form,
        disaster_id: Number(form.disaster_id),
        zone_id: Number(form.zone_id),
        team_id: Number(form.team_id),
        resources_json: { food_packets: 500, medical_kits: 50 },
      })
      setForm((f) => ({ ...f, title: '', instructions: '' }))
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function setStatus(id, status) {
    setError('')
    try {
      await api.patch(`/missions/${id}/status`, { status })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">
          {isField ? 'My Missions' : 'Mission Assignment'}
        </h2>
        <p className="text-sm text-command-600">
          {isField
            ? 'Update mission status as you move en route, on site, and complete tasks.'
            : 'Assign field teams to zones with resources and priority.'}
        </p>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      {canAssign && (
        <form onSubmit={create} className="card grid gap-3 md:grid-cols-2">
          <input
            className="rounded border px-3 py-2 text-sm"
            placeholder="Mission title"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            required
          />
          <select
            className="rounded border px-3 py-2 text-sm"
            value={form.priority}
            onChange={(e) => setForm({ ...form, priority: e.target.value })}
          >
            {['low', 'medium', 'high', 'critical'].map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
          <select
            className="rounded border px-3 py-2 text-sm"
            value={form.disaster_id}
            onChange={(e) => {
              const d = disasters.find((x) => String(x.id) === e.target.value)
              setForm({ ...form, disaster_id: e.target.value, zone_id: d?.zones?.[0]?.id || '' })
            }}
          >
            {disasters.map((d) => (
              <option key={d.id} value={d.id}>{d.title}</option>
            ))}
          </select>
          <select
            className="rounded border px-3 py-2 text-sm"
            value={form.zone_id}
            onChange={(e) => setForm({ ...form, zone_id: e.target.value })}
          >
            {zones.map((z) => (
              <option key={z.id} value={z.id}>{z.name}</option>
            ))}
          </select>
          <select
            className="rounded border px-3 py-2 text-sm"
            value={form.team_id}
            onChange={(e) => setForm({ ...form, team_id: e.target.value })}
          >
            {teams.map((t) => (
              <option key={t.id} value={t.id}>{t.name} ({t.status})</option>
            ))}
          </select>
          <textarea
            className="rounded border px-3 py-2 text-sm md:col-span-2"
            rows={2}
            placeholder="Instructions"
            value={form.instructions}
            onChange={(e) => setForm({ ...form, instructions: e.target.value })}
          />
          <button type="submit" className="btn-primary" disabled={saving}>
            {saving ? 'Creating…' : 'Create Mission'}
          </button>
        </form>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {missions.length === 0 ? (
          <div className="card text-sm text-command-500 md:col-span-2">No missions found.</div>
        ) : (
          missions.map((m) => (
            <div key={m.id} className="card space-y-2">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <p className="text-xs text-command-500">Mission #{m.id}</p>
                  <h3 className="font-semibold">{m.title}</h3>
                </div>
                <StatusBadge value={m.status} />
              </div>
              <p className="text-sm text-command-600">{m.instructions || 'No instructions'}</p>
              <div className="flex flex-wrap gap-2 text-xs">
                <StatusBadge value={m.priority} />
                <span>Disaster {m.disaster_id}</span>
                <span>Zone {m.zone_id}</span>
                <span>Team {m.team_id}</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-2">
                {(isField
                  ? [
                      ['in_progress', 'Start / On Site'],
                      ['completed', 'Complete'],
                    ]
                  : [
                      ['in_progress', 'In Progress'],
                      ['completed', 'Completed'],
                      ['cancelled', 'Cancel'],
                    ]
                ).map(([s, label]) => (
                  <button
                    key={s}
                    type="button"
                    className="btn-secondary py-1 text-xs"
                    onClick={() => setStatus(m.id, s)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
