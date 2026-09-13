import { NavLink, Outlet } from 'react-router-dom'
import { Radio, LogOut, Menu, X } from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '../hooks/useAuth'
import { ROLE_NAV, ROLE_LABELS, ROLES } from '../utils/roles'

export default function AppLayout() {
  const { user, logout, role } = useAuth()
  const navItems = ROLE_NAV[role] || ROLE_NAV[ROLES.FIELD]
  const [open, setOpen] = useState(false)
  const isField = role === ROLES.FIELD

  const title =
    role === ROLES.ADMIN
      ? 'Admin Command Center'
      : role === ROLES.COORDINATOR
        ? 'Relief Coordination Desk'
        : 'Field Operations'

  const linkClass = ({ isActive }) =>
    `mb-0.5 flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition ${
      isActive
        ? 'bg-command-800 text-white'
        : 'text-command-300 hover:bg-command-900 hover:text-white'
    }`

  const NavLinks = ({ onNavigate }) => (
    <>
      {navItems.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={['/admin', '/coordinator', '/field'].includes(to)}
          className={linkClass}
          onClick={onNavigate}
        >
          <Icon className="h-4 w-4 shrink-0" />
          {label}
        </NavLink>
      ))}
    </>
  )

  return (
    <div className="flex min-h-screen bg-command-50">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-60 flex-col border-r border-command-800 bg-command-950 text-command-100 md:flex">
        <div className="flex items-center gap-2 border-b border-command-800 px-4 py-4">
          <Radio className="h-6 w-6 text-red-400" />
          <div>
            <p className="font-display text-sm font-bold tracking-wide text-white">COMMAND CENTER</p>
            <p className="text-[10px] uppercase tracking-widest text-command-400">{ROLE_LABELS[role]}</p>
          </div>
        </div>
        <nav className="flex-1 overflow-y-auto px-2 py-3">
          <NavLinks />
        </nav>
        <div className="border-t border-command-800 p-3 text-xs text-command-400">
          <p className="truncate font-medium text-command-200">{user?.full_name}</p>
          <p className="truncate uppercase tracking-wide">{ROLE_LABELS[role]}</p>
        </div>
      </aside>

      {/* Mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-40 md:hidden">
          <button type="button" className="absolute inset-0 bg-black/40" aria-label="Close menu" onClick={() => setOpen(false)} />
          <aside className="absolute inset-y-0 left-0 flex w-64 flex-col bg-command-950 text-command-100 shadow-xl">
            <div className="flex items-center justify-between border-b border-command-800 px-4 py-4">
              <p className="font-display font-bold text-white">Menu</p>
              <button type="button" onClick={() => setOpen(false)}><X className="h-5 w-5" /></button>
            </div>
            <nav className="flex-1 overflow-y-auto px-2 py-3">
              <NavLinks onNavigate={() => setOpen(false)} />
            </nav>
          </aside>
        </div>
      )}

      <div className={`flex min-h-screen flex-1 flex-col ${isField ? 'md:pl-60' : 'md:pl-60'} pb-16 md:pb-0`}>
        <header className="sticky top-0 z-20 flex items-center justify-between border-b border-command-200 bg-white/95 px-4 py-3 backdrop-blur md:px-6">
          <div className="flex items-center gap-2">
            <button type="button" className="rounded border p-1.5 md:hidden" onClick={() => setOpen(true)}>
              <Menu className="h-5 w-5" />
            </button>
            <h1 className="font-display text-base font-semibold text-command-900 md:text-lg">{title}</h1>
          </div>
          <div className="flex items-center gap-2 md:gap-3">
            <span className="hidden sm:inline badge bg-command-100 text-command-800">{ROLE_LABELS[role]}</span>
            <button type="button" onClick={logout} className="btn-secondary py-1.5 text-xs">
              <LogOut className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Logout</span>
            </button>
          </div>
        </header>
        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>

      {/* Field mobile bottom nav */}
      {isField && (
        <nav className="fixed inset-x-0 bottom-0 z-30 flex border-t border-command-200 bg-white md:hidden">
          {navItems.slice(0, 4).map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/field'}
              className={({ isActive }) =>
                `flex flex-1 flex-col items-center gap-0.5 py-2 text-[10px] ${
                  isActive ? 'text-teal-700' : 'text-command-500'
                }`
              }
            >
              <Icon className="h-5 w-5" />
              {label.split(' ')[0]}
            </NavLink>
          ))}
        </nav>
      )}
    </div>
  )
}
