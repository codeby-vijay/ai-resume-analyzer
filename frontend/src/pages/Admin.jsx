import { useEffect, useState } from 'react'
import toast from 'react-hot-toast'
import { Users, FileText, BarChart3, Activity } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="glass-card p-6">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-brand-gradient text-white">
        <Icon size={18} />
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
    </div>
  )
}

export default function Admin() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)

  const load = () => {
    setLoading(true)
    Promise.all([api.get('/admin/stats'), api.get('/admin/users')])
      .then(([statsRes, usersRes]) => {
        setStats(statsRes.data)
        setUsers(usersRes.data)
      })
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const toggleActive = async (userId) => {
    try {
      await api.put(`/admin/users/${userId}/toggle-active`)
      toast.success('User status updated.')
      load()
    } catch {
      toast.error('Failed to update user.')
    }
  }

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <p className="text-gray-500 dark:text-gray-400">Platform-wide statistics and user management.</p>
      </div>

      {loading || !stats ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <div key={i} className="skeleton h-28 w-full" />)}
        </div>
      ) : (
        <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard icon={Users} label="Total Users" value={stats.total_users} />
          <StatCard icon={FileText} label="Resumes Uploaded" value={stats.total_resumes} />
          <StatCard icon={Activity} label="Analyses Run" value={stats.total_analyses} />
          <StatCard icon={BarChart3} label="Avg. ATS Score" value={stats.average_ats_score} />
        </div>
      )}

      <div className="glass-card p-6">
        <h2 className="mb-4 font-semibold">User Management</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-gray-100 dark:border-gray-800 text-gray-400">
                <th className="pb-3 font-medium">Name</th>
                <th className="pb-3 font-medium">Email</th>
                <th className="pb-3 font-medium">Role</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-gray-50 dark:border-gray-800/60">
                  <td className="py-3 font-medium">{u.full_name}</td>
                  <td className="py-3 text-gray-500">{u.email}</td>
                  <td className="py-3">{u.is_admin ? 'Admin' : 'User'}</td>
                  <td className="py-3">
                    <span className="rounded-full bg-green-50 px-2 py-0.5 text-xs text-green-700 dark:bg-green-500/10 dark:text-green-400">
                      Active
                    </span>
                  </td>
                  <td className="py-3">
                    <button onClick={() => toggleActive(u.id)} className="text-xs font-semibold text-brand-600 hover:underline">
                      Toggle Access
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  )
}
