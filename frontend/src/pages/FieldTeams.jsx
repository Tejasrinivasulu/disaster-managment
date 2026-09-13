import { useEffect, useState } from 'react'
import api from '../services/api'
import StatusBadge from '../components/StatusBadge'

export default function FieldTeams() {
  const [teams, setTeams] = useState([])
  const [error, setError] = useState('')
  const [form, setForm] = useState({ name: '', leader_name: '', members_count: 5, skills: '' })

  async function load() {
    try {
      const { data } = await api.get('/teams')
      setTeams(data)
    } catch (err) {
      setError(err.message)
    }
  }

  useEffect(() => { load() }, [])

  async function create(e) {
    e.preventDefault()
    try {
      await api.post('/teams', form)
      setForm({ name: '', leader_name: '', members_count: 5, skills: '' })
      await load()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="font-display text-2xl font-bold">Field Teams</h2>
        <p className="text-sm text-command-600">Manage roster, skills, location, and availability.</p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      <form onSubmit={create} className="card grid gap-3 md:grid-cols-4">
        <input className="rounded border px-3 py-2 text-sm" placeholder="Team name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input className="rounded border px-3 py-2 text-sm" placeholder="Leader" value={form.leader_name} onChange={(e) => setForm({ ...form, leader_name: e.target.value })} required />
        <input type="number" className="rounded border px-3 py-2 text-sm" placeholder="Members" value={form.members_count} onChange={(e) => setForm({ ...form, members_count: Number(e.target.value) })} />
        <button type="submit" className="btn-primary">Add Team</button>
      </form>
      <div className="card overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="border-b text-xs uppercase text-command-500">
            <tr>
              <th className="py-2 text-left">ID</th>
              <th className="py-2 text-left">Name</th>
              <th className="py-2 text-left">Leader</th>
              <th className="py-2 text-left">Members</th>
              <th className="py-2 text-left">Skills</th>
              <th className="py-2 text-left">Status</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((t) => (
              <tr key={t.id} className="border-b border-command-100">
                <td className="py-2">{t.id}</td>
                <td className="py-2 font-medium">{t.name}</td>
                <td className="py-2">{t.leader_name}</td>
                <td className="py-2">{t.members_count}</td>
                <td className="py-2">{t.skills}</td>
                <td className="py-2"><StatusBadge value={t.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
