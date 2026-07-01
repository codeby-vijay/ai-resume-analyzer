import { useState } from 'react'
import toast from 'react-hot-toast'
import Layout from '../components/Layout'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

export default function Profile() {
  const { user, setUser } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [password, setPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const payload = {}
      if (fullName && fullName !== user.full_name) payload.full_name = fullName
      if (password) payload.password = password
      const { data } = await api.put('/profile', payload)
      setUser(data)
      setPassword('')
      toast.success('Profile updated.')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Update failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Profile</h1>
        <p className="text-gray-500 dark:text-gray-400">Manage your account details.</p>
      </div>

      <div className="glass-card max-w-lg p-6">
        <div className="mb-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-brand-gradient text-xl font-bold text-white">
            {user?.full_name?.[0]?.toUpperCase()}
          </div>
          <div>
            <p className="font-semibold">{user?.full_name}</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
        </div>

        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Full Name</label>
            <input className="input-field" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">New Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="Leave blank to keep current password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <input className="input-field opacity-60" value={user?.email || ''} disabled />
          </div>
          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? 'Saving...' : 'Save Changes'}
          </button>
        </form>
      </div>
    </Layout>
  )
}
