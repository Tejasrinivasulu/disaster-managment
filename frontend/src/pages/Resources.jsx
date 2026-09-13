import { useEffect, useState } from 'react'
import { Plus, RefreshCw } from 'lucide-react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'
import { formatNumber } from '../utils/format'
import { useAuth } from '../hooks/useAuth'

const emptyResource = {
  depot_id: '',
  resource_type: 'food_packets',
  name: '',
  quantity_available: 0,
  unit: 'units',
  status: 'available',
}

export default function Resources() {
  const { role } = useAuth()
  const canEdit = role === 'admin' || role === 'relief_coordinator'
  const [resources, setResources] = useState([])
  const [depots, setDepots] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState(emptyResource)
  const [assign, setAssign] = useState({ id: null, quantity: 100, action: 'reserve' })

  async function load() {
    setLoading(true)
    setError('')
    try {
      const [res, dep] = await Promise.all([
        api.get('/resources'),
        api.get('/resources/depots'),
      ])
      setResources(res.data)
      setDepots(dep.data)
      if (!form.depot_id && dep.data.length) {
        setForm((f) => ({ ...f, depot_id: dep.data[0].id }))
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
    try {
      await api.post('/resources', {
        ...form,
        depot_id: Number(form.depot_id),
        quantity_available: Number(form.quantity_available),
      })
      setShowForm(false)
      setForm({ ...emptyResource, depot_id: depots[0]?.id || '' })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleAssign(e) {
    e.preventDefault()
    try {
      await api.post(`/resources/${assign.id}/assign`, {
        quantity: Number(assign.quantity),
        action: assign.action,
      })
      setAssign({ id: null, quantity: 100, action: 'reserve' })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this resource record?')) return
    try {
      await api.delete(`/resources/${id}`)
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  const totals = resources.reduce(
    (acc, r) => {
      acc.available += r.quantity_available
      acc.reserved += r.quantity_reserved
      acc.deployed += r.quantity_deployed
      return acc
    },
    { available: 0, reserved: 0, deployed: 0 },
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl font-bold text-command-900">
            {canEdit ? 'Resource Inventory' : 'Assigned Resources'}
          </h2>
          <p className="text-sm text-command-600">
            {canEdit
              ? 'Manage depot stocks: available, reserved, and deployed quantities.'
              : 'View reserved and deployed supplies for field operations (read-only).'}
          </p>
        </div>
        <div className="flex gap-2">
          <button type="button" className="btn-secondary" onClick={load}><RefreshCw className="h-4 w-4" /> Refresh</button>
          {canEdit && (
            <button type="button" className="btn-primary" onClick={() => setShowForm((v) => !v)}>
              <Plus className="h-4 w-4" /> Add Resource
            </button>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="card"><p className="text-xs uppercase text-command-500">Available</p><p className="mt-1 text-2xl font-semibold">{formatNumber(totals.available)}</p></div>
        <div className="card"><p className="text-xs uppercase text-command-500">Reserved</p><p className="mt-1 text-2xl font-semibold">{formatNumber(totals.reserved)}</p></div>
        <div className="card"><p className="text-xs uppercase text-command-500">Deployed</p><p className="mt-1 text-2xl font-semibold">{formatNumber(totals.deployed)}</p></div>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      {showForm && (
        <form onSubmit={handleCreate} className="card grid gap-3 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-xs uppercase text-command-500">Depot</label>
            <select className="w-full rounded border px-3 py-2 text-sm" value={form.depot_id} onChange={(e) => setForm({ ...form, depot_id: e.target.value })} required>
              {depots.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs uppercase text-command-500">Type</label>
            <select className="w-full rounded border px-3 py-2 text-sm" value={form.resource_type} onChange={(e) => setForm({ ...form, resource_type: e.target.value })}>
              {['food_packets', 'water', 'medical_kits', 'shelter', 'vehicles', 'personnel'].map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs uppercase text-command-500">Name</label>
            <input className="w-full rounded border px-3 py-2 text-sm" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
          </div>
          <div>
            <label className="mb-1 block text-xs uppercase text-command-500">Quantity</label>
            <input type="number" className="w-full rounded border px-3 py-2 text-sm" value={form.quantity_available} onChange={(e) => setForm({ ...form, quantity_available: e.target.value })} required />
          </div>
          <div>
            <label className="mb-1 block text-xs uppercase text-command-500">Unit</label>
            <input className="w-full rounded border px-3 py-2 text-sm" value={form.unit} onChange={(e) => setForm({ ...form, unit: e.target.value })} />
          </div>
          <div className="flex items-end">
            <button type="submit" className="btn-primary">Save Resource</button>
          </div>
        </form>
      )}

      {assign.id && (
        <form onSubmit={handleAssign} className="card flex flex-wrap items-end gap-3 bg-command-50">
          <p className="w-full text-sm font-semibold">Assign Resource #{assign.id}</p>
          <div>
            <label className="mb-1 block text-xs uppercase text-command-500">Action</label>
            <select className="rounded border px-3 py-2 text-sm" value={assign.action} onChange={(e) => setAssign({ ...assign, action: e.target.value })}>
              <option value="reserve">Reserve</option>
              <option value="deploy">Deploy</option>
              <option value="release">Release</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs uppercase text-command-500">Quantity</label>
            <input type="number" className="rounded border px-3 py-2 text-sm" value={assign.quantity} onChange={(e) => setAssign({ ...assign, quantity: e.target.value })} />
          </div>
          <button type="submit" className="btn-primary">Apply</button>
          <button type="button" className="btn-secondary" onClick={() => setAssign({ id: null, quantity: 100, action: 'reserve' })}>Cancel</button>
        </form>
      )}

      {loading ? (
        <p className="text-sm text-command-500">Loading resources…</p>
      ) : (
        <div className="card overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="border-b text-xs uppercase text-command-500">
              <tr>
                <th className="py-2 pr-3">ID</th>
                <th className="py-2 pr-3">Name</th>
                <th className="py-2 pr-3">Type</th>
                <th className="py-2 pr-3">Depot</th>
                <th className="py-2 pr-3">Available</th>
                <th className="py-2 pr-3">Reserved</th>
                <th className="py-2 pr-3">Deployed</th>
                <th className="py-2 pr-3">Status</th>
                <th className="py-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {resources.map((r) => {
                const depot = depots.find((d) => d.id === r.depot_id)
                return (
                  <tr key={r.id} className="border-b border-command-100">
                    <td className="py-2 pr-3">{r.id}</td>
                    <td className="py-2 pr-3 font-medium">{r.name}</td>
                    <td className="py-2 pr-3">{r.resource_type}</td>
                    <td className="py-2 pr-3">{depot?.name || r.depot_id}</td>
                    <td className="py-2 pr-3">{formatNumber(r.quantity_available)} {r.unit}</td>
                    <td className="py-2 pr-3">{formatNumber(r.quantity_reserved)}</td>
                    <td className="py-2 pr-3">{formatNumber(r.quantity_deployed)}</td>
                    <td className="py-2 pr-3"><StatusBadge value={r.status} /></td>
                    <td className="py-2">
                      {canEdit && (
                        <div className="flex gap-2">
                          <button type="button" className="text-xs font-medium text-command-700 underline" onClick={() => setAssign({ id: r.id, quantity: 100, action: 'reserve' })}>Assign</button>
                          <button type="button" className="text-xs font-medium text-red-700 underline" onClick={() => handleDelete(r.id)}>Delete</button>
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
