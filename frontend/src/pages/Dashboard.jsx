import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { UploadCloud, TrendingUp, FileText, Clock } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'
import { useAuth } from '../context/AuthContext'

function StatCard({ icon: Icon, label, value, accent }) {
  return (
    <div className="glass-card p-6">
      <div className={`mb-3 flex h-10 w-10 items-center justify-center rounded-xl text-white ${accent}`}>
        <Icon size={18} />
      </div>
      <p className="text-2xl font-bold">{value}</p>
      <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/history?limit=5')
      .then(({ data }) => setHistory(data))
      .finally(() => setLoading(false))
  }, [])

  const avgScore = history.length
    ? Math.round(history.reduce((sum, a) => sum + a.ats_score, 0) / history.length)
    : 0
  const bestScore = history.length ? Math.round(Math.max(...history.map((a) => a.ats_score))) : 0

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Welcome back, {user?.full_name?.split(' ')[0]} 👋</h1>
        <p className="text-gray-500 dark:text-gray-400">Here's a snapshot of your resume performance.</p>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-6 sm:grid-cols-3">
        <StatCard icon={FileText} label="Analyses Run" value={history.length} accent="bg-brand-gradient" />
        <StatCard icon={TrendingUp} label="Average ATS Score" value={avgScore} accent="bg-gradient-to-br from-green-500 to-emerald-600" />
        <StatCard icon={Clock} label="Best Score" value={bestScore} accent="bg-gradient-to-br from-orange-500 to-pink-600" />
      </div>

      <div className="glass-card mb-8 flex flex-col items-center justify-between gap-4 p-8 sm:flex-row">
        <div>
          <h2 className="text-lg font-semibold">Ready for your next analysis?</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Upload a resume and job description to get a fresh ATS score.
          </p>
        </div>
        <Link to="/analyze" className="btn-primary whitespace-nowrap">
          <UploadCloud size={18} />
          New Analysis
        </Link>
      </div>

      <div className="glass-card p-6">
        <h2 className="mb-4 text-lg font-semibold">Recent Analyses</h2>
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="skeleton h-14 w-full" />)}
          </div>
        ) : history.length === 0 ? (
          <p className="py-8 text-center text-sm text-gray-400">
            No analyses yet. Run your first ATS scan to see results here.
          </p>
        ) : (
          <div className="space-y-3">
            {history.map((a) => (
              <Link
                key={a.id}
                to={`/analysis/${a.id}`}
                className="flex items-center justify-between rounded-xl border border-gray-100 dark:border-gray-800 p-4 transition hover:bg-brand-50/60 dark:hover:bg-gray-800/60"
              >
                <div>
                  <p className="font-medium">Analysis #{a.id}</p>
                  <p className="text-xs text-gray-400">{new Date(a.created_at).toLocaleString()}</p>
                </div>
                <span
                  className={`rounded-full px-3 py-1 text-sm font-bold ${
                    a.ats_score >= 75
                      ? 'bg-green-50 text-green-700 dark:bg-green-500/10 dark:text-green-400'
                      : a.ats_score >= 50
                      ? 'bg-yellow-50 text-yellow-700 dark:bg-yellow-500/10 dark:text-yellow-400'
                      : 'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400'
                  }`}
                >
                  {Math.round(a.ats_score)}
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
