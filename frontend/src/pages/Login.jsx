import { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Radio } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import { homeForRole, ROLE_LABELS } from '../utils/roles'

const accounts = [
  { email: 'admin@disaster.local', password: 'admin123', role: 'admin', label: 'Admin' },
  { email: 'coordinator@disaster.local', password: 'coord123', role: 'relief_coordinator', label: 'Coordinator' },
  { email: 'field@disaster.local', password: 'field123', role: 'field_team', label: 'Field Team' },
]

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('admin@disaster.local')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const user = await login(email, password)
      const dest = location.state?.from?.pathname && location.state.from.pathname !== '/login'
        ? location.state.from.pathname
        : homeForRole(user.role)
      navigate(dest, { replace: true })
    } catch (err) {
      setError(err.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  function quickFill(account) {
    setEmail(account.email)
    setPassword(account.password)
    setError('')
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-command-950 px-4">
      <div className="w-full max-w-lg rounded-lg border border-command-700 bg-command-900 p-8 text-command-100 shadow-xl">
        <div className="mb-6 flex items-center gap-3">
          <Radio className="h-8 w-8 text-red-400" />
          <div>
            <h1 className="font-display text-xl font-bold text-white">Command Center Login</h1>
            <p className="text-xs uppercase tracking-widest text-command-400">
              Role-based access
            </p>
          </div>
        </div>

        <div className="mb-5 grid gap-2 sm:grid-cols-3">
          {accounts.map((a) => (
            <button
              key={a.email}
              type="button"
              onClick={() => quickFill(a)}
              className="rounded-md border border-command-600 bg-command-950 px-2 py-2 text-left text-xs hover:border-red-500"
            >
              <p className="font-semibold text-white">{a.label}</p>
              <p className="truncate text-command-400">{a.email}</p>
            </button>
          ))}
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-command-300">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-md border border-command-600 bg-command-950 px-3 py-2 text-sm text-white outline-none focus:border-red-500"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-command-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-command-600 bg-command-950 px-3 py-2 text-sm text-white outline-none focus:border-red-500"
              required
            />
          </div>
          {error && (
            <p className="rounded-md bg-red-950/60 px-3 py-2 text-sm text-red-300">{error}</p>
          )}
          <button type="submit" disabled={loading} className="btn-primary w-full bg-red-700 hover:bg-red-600">
            {loading ? 'Signing in…' : 'Sign In to Your Dashboard'}
          </button>
        </form>

        <div className="mt-6 rounded-md border border-command-700 bg-command-950/60 p-3 text-xs text-command-400 space-y-1">
          <p className="font-semibold text-command-300">Separate dashboards</p>
          <p>Admin → full system control</p>
          <p>Coordinator → demand, allocation, missions</p>
          <p>Field Team → assigned missions & status updates</p>
          <p className="pt-1 text-command-500">
            Passwords: admin123 / coord123 / field123
          </p>
        </div>
      </div>
    </div>
  )
}
