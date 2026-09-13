import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import { ROLES, homeForRole } from '../utils/roles'

export default function ProtectedRoute({ roles }) {
  const { loading, isAuthenticated, role } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-command-600">
        Loading…
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }

  if (roles && role !== ROLES.ADMIN && !roles.includes(role)) {
    return <Navigate to={homeForRole(role)} replace />
  }

  return <Outlet />
}
