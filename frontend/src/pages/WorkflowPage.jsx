import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import OpsWorkflow from '../components/OpsWorkflow'
import api from '../services/api'
import { formatNumber } from '../utils/format'
import { useAuth } from '../hooks/useAuth'
import { ROLES } from '../utils/roles'

export default function WorkflowPage() {
  const { role } = useAuth()
  const [stats, setStats] = useState(null)

  useEffect(() => {
    api.get('/dashboard/summary')
      .then(({ data }) => setStats(data))
      .catch(() => setStats(null))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-command-600">Operations Pipeline</p>
        <h2 className="font-display text-2xl font-bold text-command-900">Complete Disaster Response Workflow</h2>
        <p className="mt-1 text-sm text-command-600">
          This is the shared workflow for all dashboards. Click any step to open the working module.
        </p>
      </div>

      {stats && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {[
            ['Active Disasters', stats.cards.active_disasters],
            ['Affected Zones', stats.zones?.length || 0],
            ['Resources Available', stats.cards.available_resources],
            ['Predicted Demand', stats.cards.predicted_demand],
            ['Teams Active', stats.cards.field_teams_active],
          ].map(([label, value]) => (
            <div key={label} className="card py-3">
              <p className="text-xs uppercase text-command-500">{label}</p>
              <p className="mt-1 text-xl font-semibold">{formatNumber(value)}</p>
            </div>
          ))}
        </div>
      )}

      <div className="card">
        <OpsWorkflow />
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="card space-y-2">
          <h3 className="font-semibold">Admin role</h3>
          <p className="text-sm text-command-600">Oversees the full pipeline, users, resources, teams, and audit.</p>
          {role === ROLES.ADMIN && <Link to="/admin" className="text-sm underline">Open Admin Overview</Link>}
        </div>
        <div className="card space-y-2">
          <h3 className="font-semibold">Relief Coordinator</h3>
          <p className="text-sm text-command-600">Runs monitoring → prediction → allocation → logistics → missions.</p>
          {(role === ROLES.COORDINATOR || role === ROLES.ADMIN) && (
            <Link to="/coordinator" className="text-sm underline">Open Operations Desk</Link>
          )}
        </div>
        <div className="card space-y-2">
          <h3 className="font-semibold">Field Team</h3>
          <p className="text-sm text-command-600">Executes missions, navigates routes, delivers resources, submits field reports that trigger dynamic AI updates.</p>
          {(role === ROLES.FIELD || role === ROLES.ADMIN) && (
            <Link to="/field" className="text-sm underline">Open Field Dashboard</Link>
          )}
        </div>
      </div>

      <div className="rounded-lg border border-teal-200 bg-teal-50 p-4 text-sm text-teal-900">
        <p className="font-semibold">Feedback loop</p>
        <p className="mt-1">
          Field Report → Dynamic AI Update (recalculate demand) → Resource Optimization again → Logistics / Missions as needed → Operations continue.
        </p>
        {(role === ROLES.COORDINATOR || role === ROLES.ADMIN) && (
          <div className="mt-3 flex flex-wrap gap-2">
            <Link to="/demand" className="btn-primary py-1.5 text-xs">Recalculate Demand</Link>
            <Link to="/allocation" className="btn-secondary py-1.5 text-xs">Reallocate Resources</Link>
          </div>
        )}
      </div>
    </div>
  )
}
