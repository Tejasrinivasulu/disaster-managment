import { Link } from 'react-router-dom'
import { ArrowDown } from 'lucide-react'
import { OPS_WORKFLOW, linkForStep, workflowForRole } from '../utils/workflow'
import { ROLES } from '../utils/roles'
import { useAuth } from '../hooks/useAuth'

/**
 * Visual end-to-end disaster operations workflow.
 * highlightIds: optional array of step ids to emphasize for the current role.
 */
export default function OpsWorkflow({
  compact = false,
  highlightIds = null,
  title = 'Disaster Response Workflow',
  subtitle = 'From disaster occurrence through dynamic AI update — operations continue in a loop.',
  showHeader = true,
}) {
  const { role } = useAuth()
  const steps = workflowForRole(role)
  const highlights = highlightIds || (
    role === ROLES.FIELD
      ? ['field', 'report', 'logistics', 'availability', 'geo', 'mission', 'update']
      : OPS_WORKFLOW.map((s) => s.id)
  )

  return (
    <div className={compact ? 'space-y-3' : 'space-y-4'}>
      {showHeader && title && (
        <div>
          <h3 className="font-display text-lg font-bold text-command-900">{title}</h3>
          {subtitle && <p className="text-sm text-command-600">{subtitle}</p>}
          <p className="mt-1 text-xs font-medium uppercase tracking-wide text-command-500">
            Disaster Occurs → Data → Assessment → Zones → AI Demand → Vulnerability → Resources → Optimize → Logistics → Mission → Field → Report → Dynamic Update → Continue
          </p>
        </div>
      )}

      <div className="relative">
        <div className={`grid gap-3 ${compact ? 'sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'md:grid-cols-2 xl:grid-cols-3'}`}>
          {steps.map((step, idx) => {
            const Icon = step.icon
            const active = highlights.includes(step.id)
            const to = linkForStep(step, role)
            const lockedForField =
              role === ROLES.FIELD && !step.roles.includes(ROLES.FIELD) && !['geo', 'availability', 'logistics', 'mission', 'field', 'report'].includes(step.id)

            return (
              <div key={step.id} className="flex flex-col">
                <Link
                  to={lockedForField ? '/field' : to}
                  className={`rounded-lg border p-3 transition ${
                    active
                      ? 'border-command-700 bg-white shadow-sm ring-1 ring-command-200'
                      : 'border-command-200 bg-command-50/80 opacity-80'
                  } ${step.loops ? 'border-teal-600 ring-teal-200' : ''}`}
                >
                  <div className="flex items-start gap-3">
                    <div className={`rounded-md p-2 ${active ? 'bg-command-900 text-white' : 'bg-command-200 text-command-700'}`}>
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-[10px] font-bold uppercase tracking-wider text-command-500">
                        Step {step.step}{step.loops ? ' · LOOP' : ''}
                      </p>
                      <p className="font-semibold text-command-900 text-sm">{step.title}</p>
                      <p className="mt-1 text-xs text-command-600 leading-snug">{step.description}</p>
                      {!compact && (
                        <p className="mt-2 text-[11px] text-command-500">
                          → {step.outputs.join(' · ')}
                        </p>
                      )}
                    </div>
                  </div>
                </Link>
                {idx < steps.length - 1 && (
                  <div className="flex justify-center py-1 text-command-400 xl:hidden">
                    <ArrowDown className="h-4 w-4" />
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
