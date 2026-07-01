import { Routes, Route, Navigate } from 'react-router-dom'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'
import AnalysisResult from './pages/AnalysisResult'
import History from './pages/History'
import Profile from './pages/Profile'
import Admin from './pages/Admin'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/analysis/:id" element={<AnalysisResult />} />
        <Route path="/history" element={<History />} />
        <Route path="/profile" element={<Profile />} />
      </Route>

      <Route element={<ProtectedRoute adminOnly />}>
        <Route path="/admin" element={<Admin />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
