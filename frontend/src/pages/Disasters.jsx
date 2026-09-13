import { useEffect, useState } from 'react'
import { Plus, RefreshCw } from 'lucide-react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import { formatNumber } from '../utils/format'
import { useAuth } from '../hooks/useAuth'

const emptyForm = {
  disaster_type: 'Flood',
  subtype: '',
  title: '',
  description: '',
  location_name: '',
  latitude: 13.6288,
  longitude: 79.4192,
  severity: 'high',
  status: 'active',
  affected_population: 0,
}

export default function Disasters() {
  const { role } = useAuth()
  const canEdit = role === 'admin' || role === 'relief_coordinator'
  const [disasters, setDisasters] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [saving, setSaving] = useState(false)
  const [selected, setSelected] = useState(null)
  const [override, setOverride] = useState({ zoneId: null, new_priority: 'critical', reason: '' })

  async function load() {
    setLoading(true)
    setError('')
    try {
      const { data } = await api.get('/disasters')
      setDisasters(data)
      if (data.length && !selected) setSelected(data[0])
      else if (selected) {
        const refreshed = data.find((d) => d.id === selected.id)
        setSelected(refreshed || data[0] || null)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleCreate(e) {
    e.preventDefault()
    setSaving(true)
    setError('')
    try {
      await api.post('/disasters', { ...form, affected_population: Number(form.affected_population) })
      setShowForm(false)
      setForm(emptyForm)
      await load()
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  async function updateStatus(id, status) {
    try {
      await api.patch(`/disasters/${id}`, { status })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function submitOverride(e) {
    e.preventDefault()
    try {
      await api.post(`/zones/${override.zoneId}/priority-override`, {
        new_priority: override.new_priority,
        reason: override.reason,
      })
      setOverride({ zoneId: null, new_priority: 'critical', reason: '' })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-bold text-command-900">Disaster Management</h2>
          <p className="text-sm text-command-600">Track events, zones, severity, and priority overrides.</p>
        </div>
        <div className="flex gap-2">
          <button type="button" className="btn-secondary" onClick={load}>
            <RefreshCw className="h-4 w-4" /> Refresh
          </button>
          {canEdit && (
            <button type="button" className="btn-primary" onClick={() => setShowForm((v) => !v)}>
              <Plus className="h-4 w-4" /> New Disaster
            </button>
          )}
        </div>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      {showForm && (
        <form onSubmit={handleCreate} className="card grid gap-3 md:grid-cols-2">
          {['title', 'disaster_type', 'subtype', 'location_name'].map((field) => (
            <div key={field}>
              <label className="mb-1 block text-xs font-medium uppercase text-command-500">{field}</label>
              <input
                className="w-full rounded border border-command-300 px-3 py-2 text-sm"
                value={form[field]}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
                required={field === 'title' || field === 'disaster_type' || field === 'location_name'}
              />
            </div>
          ))}
          <div>
            <label className="mb-1 block text-xs font-medium uppercase text-command-500">Latitude</label>
            <input type="number" step="any" className="w-full rounded border border-command-300 px-3 py-2 text-sm" value={form.latitude} onChange={(e) => setForm({ ...form, latitude: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium uppercase text-command-500">Longitude</label>
            <input type="number" step="any" className="w-full rounded border border-command-300 px-3 py-2 text-sm" value={form.longitude} onChange={(e) => setForm({ ...form, longitude: Number(e.target.value) })} required />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium uppercase text-command-500">Severity</label>
            <select className="w-full rounded border border-command-300 px-3 py-2 text-sm" value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })}>
              {['low', 'medium', 'high', 'critical'].map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium uppercase text-command-500">Affected Population</label>
            <input type="number" className="w-full rounded border border-command-300 px-3 py-2 text-sm" value={form.affected_population} onChange={(e) => setForm({ ...form, affected_population: e.target.value })} />
          </div>
          <div className="md:col-span-2">
            <label className="mb-1 block text-xs font-medium uppercase text-command-500">Description</label>
            <textarea className="w-full rounded border border-command-300 px-3 py-2 text-sm" rows={2} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div className="md:col-span-2">
            <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Create Disaster'}</button>
          </div>
        </form>
      )}

      {loading ? (
        <p className="text-sm text-command-500">Loading disasters…</p>
      ) : disasters.length === 0 ? (
        <div className="card text-sm text-command-500">No disasters recorded yet.</div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-5">
          <div className="space-y-3 lg:col-span-2">
            {disasters.map((d) => (
              <button
                key={d.id}
                type="button"
                onClick={() => setSelected(d)}
                className={`card w-full text-left transition ${selected?.id === d.id ? 'ring-2 ring-command-700' : ''}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-command-900">{d.title}</p>
                    <p className="text-xs text-command-500">ID {d.id} · {d.disaster_type}{d.subtype ? ` / ${d.subtype}` : ''}</p>
                  </div>
                  <StatusBadge value={d.status} />
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-xs text-command-600">
                  <StatusBadge value={d.severity} />
                  <span>{d.location_name}</span>
                  <span>Pop {formatNumber(d.affected_population)}</span>
                </div>
              </button>
            ))}
          </div>

          {selected && (
            <div className="card space-y-4 lg:col-span-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <h3 className="text-lg font-semibold">{selected.title}</h3>
                  <p className="text-sm text-command-600">{selected.description || 'No description'}</p>
                </div>
                {canEdit && (
                  <select
                    className="rounded border border-command-300 px-2 py-1 text-sm"
                    value={selected.status}
                    onChange={(e) => updateStatus(selected.id, e.target.value)}
                  >
                    {['active', 'monitoring', 'recovery', 'closed'].map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                )}
              </div>
              <dl className="grid grid-cols-2 gap-3 text-sm md:grid-cols-3">
                <div><dt className="text-command-500">Location</dt><dd>{selected.location_name}</dd></div>
                <div><dt className="text-command-500">Coordinates</dt><dd>{selected.latitude.toFixed(4)}, {selected.longitude.toFixed(4)}</dd></div>
                <div><dt className="text-command-500">Affected</dt><dd>{formatNumber(selected.affected_population)}</dd></div>
              </dl>

              <div>
                <h4 className="mb-2 font-semibold">Affected Zones</h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-left text-sm">
                    <thead className="border-b text-xs uppercase text-command-500">
                      <tr>
                        <th className="py-2 pr-3">Zone</th>
                        <th className="py-2 pr-3">Population</th>
                        <th className="py-2 pr-3">Severity</th>
                        <th className="py-2 pr-3">Priority</th>
                        <th className="py-2">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(selected.zones || []).map((z) => (
                        <tr key={z.id} className="border-b border-command-100">
                          <td className="py-2 pr-3 font-medium">{z.name}</td>
                          <td className="py-2 pr-3">{formatNumber(z.population)}</td>
                          <td className="py-2 pr-3"><StatusBadge value={z.severity} /></td>
                          <td className="py-2 pr-3">
                            <StatusBadge value={z.priority} />
                            {z.priority_override && <span className="ml-1 text-[10px] text-red-600">OVERRIDE</span>}
                          </td>
                          <td className="py-2">
                            {canEdit && (
                              <button
                                type="button"
                                className="text-xs font-medium text-command-700 underline"
                                onClick={() => setOverride({ zoneId: z.id, new_priority: 'critical', reason: '' })}
                              >
                                Override Priority
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {override.zoneId && (
                <form onSubmit={submitOverride} className="rounded-md border border-amber-200 bg-amber-50 p-3 space-y-2">
                  <p className="text-sm font-semibold text-amber-900">Override Priority — Zone #{override.zoneId}</p>
                  <select className="w-full rounded border border-amber-300 px-2 py-1.5 text-sm" value={override.new_priority} onChange={(e) => setOverride({ ...override, new_priority: e.target.value })}>
                    {['low', 'medium', 'high', 'critical'].map((p) => <option key={p} value={p}>{p}</option>)}
                  </select>
                  <input
                    className="w-full rounded border border-amber-300 px-2 py-1.5 text-sm"
                    placeholder="Reason for override"
                    value={override.reason}
                    onChange={(e) => setOverride({ ...override, reason: e.target.value })}
                    required
                  />
                  <div className="flex gap-2">
                    <button type="submit" className="btn-primary py-1.5 text-xs">Save Override</button>
                    <button type="button" className="btn-secondary py-1.5 text-xs" onClick={() => setOverride({ zoneId: null, new_priority: 'critical', reason: '' })}>Cancel</button>
                  </div>
                </form>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
