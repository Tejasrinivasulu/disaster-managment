const styles = {
  critical: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  medium: 'bg-amber-100 text-amber-800',
  low: 'bg-green-100 text-green-800',
  active: 'bg-red-100 text-red-800',
  monitoring: 'bg-blue-100 text-blue-800',
  recovery: 'bg-indigo-100 text-indigo-800',
  closed: 'bg-slate-100 text-slate-700',
  available: 'bg-green-100 text-green-800',
  reserved: 'bg-amber-100 text-amber-800',
  deployed: 'bg-blue-100 text-blue-800',
  depleted: 'bg-slate-200 text-slate-700',
  assigned: 'bg-blue-100 text-blue-800',
  en_route: 'bg-indigo-100 text-indigo-800',
  on_site: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  planned: 'bg-slate-100 text-slate-700',
  in_progress: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-slate-200 text-slate-600',
}

export default function StatusBadge({ value }) {
  if (!value) return null
  const key = String(value).toLowerCase()
  const cls = styles[key] || 'bg-command-100 text-command-800'
  return <span className={`badge ${cls}`}>{String(value).replace('_', ' ')}</span>
}
