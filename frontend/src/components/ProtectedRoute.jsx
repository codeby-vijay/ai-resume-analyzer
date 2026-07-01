import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import PageLoader from './PageLoader'

export default function ProtectedRoute({ adminOnly = false }) {
  const { user, loading } = useAuth()

  if (loading) return <PageLoader />
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && !user.is_admin) return <Navigate to="/dashboard" replace />

  return <Outlet />
}
