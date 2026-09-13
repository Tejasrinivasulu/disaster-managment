import { useEffect, useState } from 'react'
import api from '../../services/api'

export default function AdminAudit() {
  const [logs, setLogs] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/admin/audit-logs?limit=150')
      .then(({ data }) => setLogs(data))
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold uppercase tracking-widest text-red-700">Admin</p>
        <h2 className="font-display text-2xl font-bold">Audit Logs</h2>
        <p className="text-sm text-command-600">Track administrative and field actions across the system.</p>
      </div>
      {error && <div className="rounded-md bg-red-50 p-3 text-sm text-red-800">{error}</div>}
      <div className="card overflow-x-auto">
        {logs.length === 0 ? (
          <p className="text-sm text-command-500">No audit events yet. Creating users or submitting field reports will appear here.</p>
        ) : (
          <table className="min-w-full text-sm">
            <thead className="border-b text-xs uppercase text-command-500">
              <tr>
                <th className="py-2 text-left">Time</th>
                <th className="py-2 text-left">User</th>
                <th className="py-2 text-left">Action</th>
                <th className="py-2 text-left">Entity</th>
                <th className="py-2 text-left">Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id} className="border-b border-command-100 align-top">
                  <td className="py-2 whitespace-nowrap text-xs">{l.created_at ? new Date(l.created_at).toLocaleString() : '—'}</td>
                  <td className="py-2">{l.user_id ?? '—'}</td>
                  <td className="py-2 font-medium">{l.action}</td>
                  <td className="py-2">{l.entity_type} #{l.entity_id}</td>
                  <td className="py-2 text-xs text-command-600 max-w-md">{l.details}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
