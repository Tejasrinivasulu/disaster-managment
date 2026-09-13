import { useAuth } from '../hooks/useAuth'
import { ROLE_LABELS, homeForRole } from '../utils/roles'
import { Link } from 'react-router-dom'

export default function Settings() {
  const { user, role } = useAuth()
  return (
    <div className="space-y-4">
      <h2 className="font-display text-2xl font-bold">Settings</h2>
      <div className="card space-y-2 text-sm">
        <p><span className="text-command-500">Signed in as:</span> {user?.full_name} ({user?.email})</p>
        <p><span className="text-command-500">Role:</span> {ROLE_LABELS[role] || role}</p>
        <p>
          <span className="text-command-500">Home dashboard:</span>{' '}
          <Link className="underline" to={homeForRole(role)}>{homeForRole(role)}</Link>
        </p>
        <div className="rounded border border-command-200 bg-command-50 p-3 text-command-700">
          <p className="font-medium">Access by role</p>
          <ul className="mt-1 list-disc pl-5 text-xs space-y-1">
            <li>Admin — full system modules</li>
            <li>Relief Coordinator — disasters, demand, allocation, logistics, missions, reports</li>
            <li>Field Team — missions status, map, assigned resources, field reports</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
