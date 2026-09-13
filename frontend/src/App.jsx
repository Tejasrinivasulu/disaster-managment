import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './layouts/AppLayout'
import ProtectedRoute from './components/ProtectedRoute'
import RoleHome from './pages/RoleHome'
import AdminDashboard from './pages/dashboards/AdminDashboard'
import AdminUsers from './pages/dashboards/AdminUsers'
import AdminAudit from './pages/dashboards/AdminAudit'
import CoordinatorDashboard from './pages/dashboards/CoordinatorDashboard'
import FieldDashboard from './pages/dashboards/FieldDashboard'
import FieldReportsPage from './pages/FieldReportsPage'
import Disasters from './pages/Disasters'
import ImpactMap from './pages/ImpactMap'
import DemandPrediction from './pages/DemandPrediction'
import Resources from './pages/Resources'
import Allocation from './pages/Allocation'
import Logistics from './pages/Logistics'
import FieldTeams from './pages/FieldTeams'
import Missions from './pages/Missions'
import Scenarios from './pages/Scenarios'
import Reports from './pages/Reports'
import Settings from './pages/Settings'
import WorkflowPage from './pages/WorkflowPage'
import Login from './pages/Login'
import { useAuth } from './hooks/useAuth'
import { ROLES, homeForRole } from './utils/roles'

function PublicOnly({ children }) {
  const { isAuthenticated, loading, role } = useAuth()
  if (loading) return null
  if (isAuthenticated) return <Navigate to={homeForRole(role)} replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<PublicOnly><Login /></PublicOnly>} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<RoleHome />} />

          <Route element={<ProtectedRoute roles={[ROLES.ADMIN]} />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/users" element={<AdminUsers />} />
            <Route path="/admin/audit" element={<AdminAudit />} />
          </Route>

          <Route element={<ProtectedRoute roles={[ROLES.COORDINATOR, ROLES.ADMIN]} />}>
            <Route path="/coordinator" element={<CoordinatorDashboard />} />
            <Route path="/disasters" element={<Disasters />} />
            <Route path="/demand" element={<DemandPrediction />} />
            <Route path="/allocation" element={<Allocation />} />
            <Route path="/logistics" element={<Logistics />} />
            <Route path="/teams" element={<FieldTeams />} />
            <Route path="/scenarios" element={<Scenarios />} />
            <Route path="/reports" element={<Reports />} />
          </Route>

          <Route element={<ProtectedRoute roles={[ROLES.FIELD, ROLES.ADMIN]} />}>
            <Route path="/field" element={<FieldDashboard />} />
          </Route>

          <Route path="/map" element={<ImpactMap />} />
          <Route path="/resources" element={<Resources />} />
          <Route path="/missions" element={<Missions />} />
          <Route path="/workflow" element={<WorkflowPage />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/field/reports" element={<FieldReportsPage />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
