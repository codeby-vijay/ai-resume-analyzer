import { NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, UploadCloud, History, User, Shield, Moon, Sun, LogOut, FileScan,
} from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { useTheme } from '../context/ThemeContext'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyze', label: 'Analyze Resume', icon: UploadCloud },
  { to: '/history', label: 'History', icon: History },
  { to: '/profile', label: 'Profile', icon: User },
]

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const { dark, toggleTheme } = useTheme()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-brand-50 dark:from-gray-950 dark:via-gray-950 dark:to-gray-900">
      <div className="mx-auto flex max-w-7xl">
        <aside className="sticky top-0 hidden h-screen w-64 flex-col justify-between border-r border-gray-100 dark:border-gray-800 p-6 md:flex">
          <div>
            <div className="mb-10 flex items-center gap-2">
              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-gradient text-white">
                <FileScan size={18} />
              </div>
              <span className="text-lg font-bold">ResumeAI</span>
            </div>
            <nav className="space-y-1">
              {navItems.map(({ to, label, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                      isActive
                        ? 'bg-brand-gradient text-white shadow-md shadow-brand-600/20'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-brand-50 dark:hover:bg-gray-800'
                    }`
                  }
                >
                  <Icon size={18} />
                  {label}
                </NavLink>
              ))}
              {user?.is_admin && (
                <NavLink
                  to="/admin"
                  className={({ isActive }) =>
                    `flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition ${
                      isActive
                        ? 'bg-brand-gradient text-white shadow-md shadow-brand-600/20'
                        : 'text-gray-600 dark:text-gray-300 hover:bg-brand-50 dark:hover:bg-gray-800'
                    }`
                  }
                >
                  <Shield size={18} />
                  Admin
                </NavLink>
              )}
            </nav>
          </div>

          <div className="space-y-3">
            <button onClick={toggleTheme} className="btn-secondary w-full">
              {dark ? <Sun size={16} /> : <Moon size={16} />}
              {dark ? 'Light Mode' : 'Dark Mode'}
            </button>
            <div className="glass-card flex items-center gap-3 p-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-brand-gradient text-sm font-semibold text-white">
                {user?.full_name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate text-sm font-semibold">{user?.full_name}</p>
                <p className="truncate text-xs text-gray-500 dark:text-gray-400">{user?.email}</p>
              </div>
              <button onClick={handleLogout} title="Log out" className="text-gray-400 hover:text-red-500">
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </aside>

        <main className="min-h-screen flex-1 p-4 md:p-8">
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            {children}
          </motion.div>
        </main>
      </div>
    </div>
  )
}
