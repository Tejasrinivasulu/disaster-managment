import {
  LayoutDashboard,
  AlertTriangle,
  Map,
  Brain,
  Package,
  GitBranch,
  Truck,
  Users,
  ClipboardList,
  FlaskConical,
  FileBarChart,
  Settings,
  Shield,
  UserCog,
  ScrollText,
  FileWarning,
  GitMerge,
} from 'lucide-react'

export const ROLES = {
  ADMIN: 'admin',
  COORDINATOR: 'relief_coordinator',
  FIELD: 'field_team',
}

export const ROLE_NAV = {
  [ROLES.ADMIN]: [
    { to: '/admin', label: 'Admin Overview', icon: Shield },
    { to: '/workflow', label: 'Full Workflow', icon: GitMerge },
    { to: '/admin/users', label: 'Manage Users', icon: UserCog },
    { to: '/disasters', label: 'Manage Disasters', icon: AlertTriangle },
    { to: '/resources', label: 'Manage Resources', icon: Package },
    { to: '/teams', label: 'Manage Teams', icon: Users },
    { to: '/missions', label: 'Missions', icon: ClipboardList },
    { to: '/reports', label: 'Reports', icon: FileBarChart },
    { to: '/admin/audit', label: 'Audit Logs', icon: ScrollText },
    { to: '/settings', label: 'System Settings', icon: Settings },
  ],
  [ROLES.COORDINATOR]: [
    { to: '/coordinator', label: 'Operations Desk', icon: LayoutDashboard },
    { to: '/workflow', label: 'Full Workflow', icon: GitMerge },
    { to: '/disasters', label: 'Disaster Monitoring', icon: AlertTriangle },
    { to: '/map', label: 'Impact Map', icon: Map },
    { to: '/demand', label: 'AI Demand Prediction', icon: Brain },
    { to: '/resources', label: 'Resources', icon: Package },
    { to: '/allocation', label: 'Resource Allocation', icon: GitBranch },
    { to: '/logistics', label: 'Logistics & Routes', icon: Truck },
    { to: '/missions', label: 'Assign Missions', icon: ClipboardList },
    { to: '/teams', label: 'Field Teams', icon: Users },
    { to: '/scenarios', label: 'Scenarios', icon: FlaskConical },
    { to: '/reports', label: 'Reports', icon: FileBarChart },
    { to: '/settings', label: 'Settings', icon: Settings },
  ],
  [ROLES.FIELD]: [
    { to: '/field', label: 'My Dashboard', icon: LayoutDashboard },
    { to: '/workflow', label: 'Workflow View', icon: GitMerge },
    { to: '/missions', label: 'My Missions', icon: ClipboardList },
    { to: '/field/reports', label: 'Field Reports', icon: FileWarning },
    { to: '/map', label: 'Navigate / Map', icon: Map },
    { to: '/resources', label: 'Resource Manifest', icon: Package },
    { to: '/settings', label: 'Settings', icon: Settings },
  ],
}

export const ROLE_HOME = {
  [ROLES.ADMIN]: '/admin',
  [ROLES.COORDINATOR]: '/coordinator',
  [ROLES.FIELD]: '/field',
}

export const ROLE_LABELS = {
  [ROLES.ADMIN]: 'System Admin',
  [ROLES.COORDINATOR]: 'Relief Coordinator',
  [ROLES.FIELD]: 'Field Team',
}

export function canAccess(role, path) {
  if (!role) return false
  if (role === ROLES.ADMIN) return true
  const allowed = ROLE_NAV[role] || []
  return allowed.some((item) => path === item.to || path.startsWith(`${item.to}/`))
}

export function homeForRole(role) {
  return ROLE_HOME[role] || '/login'
}
