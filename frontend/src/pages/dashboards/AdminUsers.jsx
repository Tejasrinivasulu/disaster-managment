import { useEffect, useState } from 'react'
import api from '../../services/api'
import StatusBadge from '../../components/StatusBadge'

export default function AdminUsers() {
  const [users, setUsers] = useState([])
  const [error, setError] = useState('')
  const [form, setForm] = useState({
    email: '',
    full_name: '',
    password: '',
    role: 'field_team',
  })

  async function load() {
    const { data } = await api.get('/admin/users')
    setUsers(data)
  }

  useEffect(() => {
    load().catch((err) => setError(err.message))
  }, [])

  async function createUser(e) {
    e.preventDefault()
    setError('')
    try {
      await api.post('/admin/users', form)
      setForm({ email: '', full_name: '', password: '', role: 'field_team' })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function toggleActive(user) {
    try {
      await api.patch(`/admin/users/${user.id}`, { is_active: !user.is_active })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  async function changeRole(user, role) {
    try {
      await api.patch(`/admin/users/${user.id}`, { role })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-red-700">Admin</p>
        <h2 className="font-display text-2xl font-bold">User Management</h2>
        <p className="text-sm text-command-600">Create accounts and assign Admin / Coordinator / Field Team roles.</p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      <form onSubmit={createUser} className="card grid gap-3 md:grid-cols-2">
        <input className="rounded border px-3 py-2 text-sm" placeholder="Full name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} required />
        <input type="email" className="rounded border px-3 py-2 text-sm" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input type="password" className="rounded border px-3 py-2 text-sm" placeholder="Password (min 6)" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        <select className="rounded border px-3 py-2 text-sm" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
          <option value="admin">admin</option>
          <option value="relief_coordinator">relief_coordinator</option>
          <option value="field_team">field_team</option>
        </select>
        <button type="submit" className="btn-primary md:col-span-2">Create User</button>
      </form>

      <div className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b text-xs uppercase text-command-500">
            <tr>
              <th className="py-2 text-left">ID</th>
              <th className="py-2 text-left">Name</th>
              <th className="py-2 text-left">Email</th>
              <th className="py-2 text-left">Role</th>
              <th className="py-2 text-left">Status</th>
              <th className="py-2 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id} className="border-b border-command-100">
                <td className="py-2">{u.id}</td>
                <td className="py-2 font-medium">{u.full_name}</td>
                <td className="py-2">{u.email}</td>
                <td className="py-2">
                  <select className="rounded border px-2 py-1 text-xs" value={u.role} onChange={(e) => changeRole(u, e.target.value)}>
                    <option value="admin">admin</option>
                    <option value="relief_coordinator">relief_coordinator</option>
                    <option value="field_team">field_team</option>
                  </select>
                </td>
                <td className="py-2">
                  <StatusBadge value={u.is_active ? 'available' : 'cancelled'} />
                </td>
                <td className="py-2">
                  <button type="button" className="text-xs underline" onClick={() => toggleActive(u)}>
                    {u.is_active ? 'Deactivate' : 'Activate'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
