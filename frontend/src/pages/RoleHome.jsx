import { Navigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { homeForRole } from '../utils/roles'

/** Redirect `/` to the correct role dashboard. */
export default function RoleHome() {
  const { role, loading } = useAuth()
  if (loading) {
    return <div className="p-8 text-sm text-command-500">Loading workspace…</div>
  }
  return <Navigate to={homeForRole(role)} replace />
}
