import { Link } from 'react-router-dom'
import { opsLink } from '../utils/opsLinks'

const PIPELINE = [
  { id: 'demand', label: 'Predict Demand', to: '/demand' },
  { id: 'resources', label: 'Check Stock', to: '/resources' },
  { id: 'allocate', label: 'Allocate Resources', to: '/allocation' },
  { id: 'logistics', label: 'Plan Route', to: '/logistics' },
  { id: 'mission', label: 'Assign Mission', to: '/missions' },
  { id: 'field', label: 'Field Response', to: '/missions' },
]

/**
 * Compact end-to-end ops strip highlighting the current step.
 */
export default function EndToEndPipeline({
  activeId = 'allocate',
  disasterId = '',
  zoneId = '',
  className = '',
}) {
  return (
    <div className={`rounded-lg border border-command-200 bg-command-50/80 p-3 ${className}`}>
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-command-500">
        End-to-end relief pipeline
      </p>
      <ol className="flex flex-wrap items-center gap-1.5 text-xs">
        {PIPELINE.map((step, i) => {
          const active = step.id === activeId
          const done = PIPELINE.findIndex((s) => s.id === activeId) > i
          return (
            <li key={step.id} className="flex items-center gap-1.5">
              {i > 0 && <span className="text-command-300">→</span>}
              <Link
                to={opsLink(step.to, { disasterId, zoneId })}
                className={[
                  'rounded-full px-2.5 py-1 font-medium transition',
                  active
                    ? 'bg-command-800 text-white'
                    : done
                      ? 'bg-teal-100 text-teal-900'
                      : 'bg-white text-command-700 ring-1 ring-command-200 hover:bg-command-100',
                ].join(' ')}
              >
                {i + 1}. {step.label}
              </Link>
            </li>
          )
        })}
      </ol>
    </div>
  )
}
