import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Inbox } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function History() {
  const [analyses, setAnalyses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/history?limit=100')
      .then(({ data }) => setAnalyses(data))
      .finally(() => setLoading(false))
  }, [])

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Analysis History</h1>
        <p className="text-gray-500 dark:text-gray-400">All your past resume analyses in one place.</p>
      </div>

      <div className="glass-card p-6">
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3, 4].map((i) => <div key={i} className="skeleton h-16 w-full" />)}
          </div>
        ) : analyses.length === 0 ? (
          <div className="flex flex-col items-center py-16 text-center text-gray-400">
            <Inbox size={40} className="mb-3" />
            <p>No analyses yet.</p>
            <Link to="/analyze" className="mt-3 btn-primary">Run your first analysis</Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-gray-100 dark:border-gray-800 text-gray-400">
                  <th className="pb-3 font-medium">ID</th>
                  <th className="pb-3 font-medium">Date</th>
                  <th className="pb-3 font-medium">Skill Match</th>
                  <th className="pb-3 font-medium">Formatting</th>
                  <th className="pb-3 font-medium">ATS Score</th>
                </tr>
              </thead>
              <tbody>
                {analyses.map((a) => (
                  <tr
                    key={a.id}
                    className="cursor-pointer border-b border-gray-50 dark:border-gray-800/60 transition hover:bg-brand-50/60 dark:hover:bg-gray-800/60"
                    onClick={() => (window.location.href = `/analysis/${a.id}`)}
                  >
                    <td className="py-3 font-medium">#{a.id}</td>
                    <td className="py-3 text-gray-500">{new Date(a.created_at).toLocaleDateString()}</td>
                    <td className="py-3">{Math.round(a.skill_match_score)}</td>
                    <td className="py-3">{Math.round(a.formatting_score)}</td>
                    <td className="py-3">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-bold ${
                          a.ats_score >= 75
                            ? 'bg-green-50 text-green-700 dark:bg-green-500/10 dark:text-green-400'
                            : a.ats_score >= 50
                            ? 'bg-yellow-50 text-yellow-700 dark:bg-yellow-500/10 dark:text-yellow-400'
                            : 'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400'
                        }`}
                      >
                        {Math.round(a.ats_score)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  )
}
