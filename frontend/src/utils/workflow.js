import {
  Database,
  Map,
  Layers,
  Brain,
  Scale,
  Package,
  GitBranch,
  Truck,
  ClipboardList,
  Users,
  FileWarning,
  RefreshCw,
} from 'lucide-react'
import { ROLES } from './roles'

/**
 * End-to-end disaster response operations workflow
 * shared across Admin, Coordinator, and Field dashboards.
 */
export const OPS_WORKFLOW = [
  {
    id: 'input',
    step: 1,
    title: 'Disaster Data Input',
    description: 'GDACS / USGS / NDMA, satellite feeds, or local dataset',
    to: '/disasters',
    icon: Database,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR],
    outputs: ['Event type', 'Location', 'Time'],
  },
  {
    id: 'geo',
    step: 2,
    title: 'Geospatial Assessment',
    description: 'Location, population, damage, severity, vulnerability',
    to: '/map',
    icon: Map,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR, ROLES.FIELD],
    outputs: ['Impact map', 'Severity score'],
  },
  {
    id: 'zones',
    step: 3,
    title: 'Affected Zone Creation',
    description: 'Zone A Critical · Zone B High · Zone C Medium',
    to: '/disasters',
    icon: Layers,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR],
    outputs: ['Priority zones'],
  },
  {
    id: 'predict',
    step: 4,
    title: 'AI Demand Prediction',
    description: 'Food, water, medical kits, shelter',
    to: '/demand',
    icon: Brain,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR],
    outputs: ['Base demand'],
  },
  {
    id: 'vulnerability',
    step: 5,
    title: 'Vulnerability Weighting',
    description: 'Population, children/elderly, medical dependency, vulnerability score',
    to: '/demand',
    icon: Scale,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR],
    outputs: ['Final demand'],
  },
  {
    id: 'availability',
    step: 6,
    title: 'Resource Availability',
    description: 'Food, water, medical, shelter, vehicles, teams',
    to: '/resources',
    icon: Package,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR, ROLES.FIELD],
    outputs: ['Depot stock'],
  },
  {
    id: 'optimize',
    step: 7,
    title: 'Resource Allocation',
    description: 'Demand vs stock → priority split → reserve inventory for zones',
    to: '/allocation',
    icon: GitBranch,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR],
    outputs: ['Allocation plan', 'Reserved stock'],
  },
  {
    id: 'logistics',
    step: 8,
    title: 'Logistics & Routing',
    description: 'Depot → zone, best available route, vehicle assignment',
    to: '/logistics',
    icon: Truck,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR, ROLES.FIELD],
    outputs: ['Route + ETA'],
  },
  {
    id: 'mission',
    step: 9,
    title: 'Mission Assignment',
    description: 'Team + zone + resources + instructions',
    to: '/missions',
    icon: ClipboardList,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR],
    outputs: ['Mission card'],
  },
  {
    id: 'field',
    step: 10,
    title: 'Field Response',
    description: 'En Route → On Site → Completed',
    to: '/field',
    icon: Users,
    roles: [ROLES.FIELD, ROLES.ADMIN, ROLES.COORDINATOR],
    fieldTo: '/field',
    coordTo: '/missions',
    outputs: ['Status updates'],
  },
  {
    id: 'report',
    step: 11,
    title: 'Field Report',
    description: 'New damage, population, resource requirement',
    to: '/field/reports',
    icon: FileWarning,
    roles: [ROLES.FIELD, ROLES.ADMIN, ROLES.COORDINATOR],
    fieldTo: '/field',
    coordTo: '/field/reports',
    outputs: ['Ground truth'],
  },
  {
    id: 'update',
    step: 12,
    title: 'Dynamic AI Update',
    description: 'Recalculate demand → reallocate → continue operations',
    to: '/allocation',
    icon: RefreshCw,
    roles: [ROLES.ADMIN, ROLES.COORDINATOR],
    outputs: ['Updated demand', 'New allocation'],
    loops: true,
  },
]

export function workflowForRole(role) {
  if (role === ROLES.ADMIN) return OPS_WORKFLOW
  if (role === ROLES.COORDINATOR) {
    return OPS_WORKFLOW.filter((s) => s.roles.includes(ROLES.COORDINATOR))
  }
  // Field team sees the operational chain with their steps highlighted
  return OPS_WORKFLOW
}

export function linkForStep(step, role) {
  if (role === ROLES.FIELD) {
    if (step.fieldTo) return step.fieldTo
    if ([ROLES.FIELD].some((r) => step.roles.includes(r))) return step.to
    return '/field'
  }
  if (step.coordTo && role === ROLES.COORDINATOR) return step.coordTo
  return step.to
}
