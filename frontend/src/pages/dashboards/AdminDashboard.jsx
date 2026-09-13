import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../../services/api'
import { formatNumber } from '../../utils/format'
import { useAuth } from '../../hooks/useAuth'
import StatusBadge from '../../components/StatusBadge'
import OpsWorkflow from '../../components/OpsWorkflow'

export default function AdminDashboard() {
  const { user } = useAuth()
  const [overview, setOverview] = useState(null)
  const [summary, setSummary] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([api.get('/admin/overview'), api.get('/dashboard/summary')])
      .then(([o, s]) => {
        setOverview(o.data)
        setSummary(s.data)
      })
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-red-700">Admin</p>
        <h2 className="font-display text-2xl font-bold">System Overview</h2>
        <p className="text-sm text-command-600">
          Highest-level control across the full disaster response workflow. Signed in as {user?.full_name}.
        </p>
      </div>

      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}

      <div className="card">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-semibold">System-wide workflow (all roles)</h3>
          <Link to="/workflow" className="text-xs underline">Open workflow board</Link>
        </div>
        <OpsWorkflow compact />
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ['Manage Users', '/admin/users', 'Create roles & activate accounts'],
          ['Manage Disasters', '/disasters', 'Disaster data input & zones'],
          ['Manage Resources', '/resources', 'Availability & depots'],
          ['Manage Teams', '/teams', 'Field team roster'],
          ['Overall Operations', '/missions', 'Missions across system'],
          ['Reports', '/reports', 'Post-event analytics + PDF'],
          ['Audit Logs', '/admin/audit', 'Who changed what'],
          ['System Settings', '/settings', 'Account & access'],
        ].map(([label, to, desc]) => (
          <Link key={to} to={to} className="card hover:border-command-500 transition">
            <p className="font-semibold text-command-900">{label}</p>
            <p className="mt-1 text-xs text-command-500">{desc}</p>
          </Link>
        ))}
      </div>

      {overview && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {[
            ['Users', overview.users],
            ['Active Users', overview.active_users],
            ['Disasters', overview.disasters],
            ['Depots', overview.depots],
            ['Resources', overview.resources],
            ['Teams', overview.teams],
            ['Missions', overview.missions],
            ['Audit Events', overview.audit_events],
          ].map(([label, value]) => (
            <div key={label} className="card">
              <p className="text-xs uppercase text-command-500">{label}</p>
              <p className="mt-2 text-2xl font-semibold">{formatNumber(value)}</p>
            </div>
          ))}
        </div>
      )}

      {summary && (
        <div className="card">
          <h3 className="mb-3 font-semibold">Live operations snapshot</h3>
          <div className="grid gap-3 sm:grid-cols-3 text-sm">
            <p>Active disasters: <strong>{summary.cards.active_disasters}</strong></p>
            <p>Affected population: <strong>{formatNumber(summary.cards.affected_population)}</strong></p>
            <p>Teams active: <strong>{summary.cards.field_teams_active}</strong></p>
          </div>
          <div className="mt-4 space-y-2">
            {summary.critical_zones?.slice(0, 4).map((z) => (
              <div key={z.id} className="flex justify-between border-b border-command-100 py-1 text-sm">
                <span>{z.name}</span>
                <StatusBadge value={z.priority} />
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
