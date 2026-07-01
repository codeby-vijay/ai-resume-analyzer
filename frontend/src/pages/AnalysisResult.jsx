import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Download, Lightbulb, ThumbsUp, ThumbsDown, GraduationCap } from 'lucide-react'
import toast from 'react-hot-toast'
import Layout from '../components/Layout'
import ScoreGauge from '../components/ScoreGauge'
import ScoreBreakdownChart from '../components/ScoreBreakdownChart'
import { SkillBadgeList } from '../components/SkillBadgeList'
import api from '../api/client'

function ListCard({ icon: Icon, title, items, tone }) {
  return (
    <div className="glass-card p-6">
      <div className="mb-3 flex items-center gap-2">
        <Icon size={18} className={tone} />
        <h3 className="font-semibold">{title}</h3>
      </div>
      <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-300">
        {items.map((item, i) => (
          <li key={i} className="flex gap-2">
            <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-current opacity-50" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function AnalysisResult() {
  const { id } = useParams()
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(true)
  const [downloading, setDownloading] = useState(false)

  useEffect(() => {
    api.get(`/analyses/${id}`)
      .then(({ data }) => setAnalysis(data))
      .catch(() => toast.error('Could not load analysis.'))
      .finally(() => setLoading(false))
  }, [id])

  const downloadReport = async () => {
    setDownloading(true)
    try {
      const response = await api.get(`/reports/${id}`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `ats_report_${id}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch {
      toast.error('Failed to download report.')
    } finally {
      setDownloading(false)
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="space-y-4">
          <div className="skeleton h-8 w-64" />
          <div className="skeleton h-64 w-full" />
        </div>
      </Layout>
    )
  }

  if (!analysis) {
    return (
      <Layout>
        <p className="text-gray-500">Analysis not found. <Link to="/history" className="text-brand-600">Back to history</Link></p>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold">Analysis #{analysis.id}</h1>
          <p className="text-gray-500 dark:text-gray-400">{new Date(analysis.created_at).toLocaleString()}</p>
        </div>
        <button onClick={downloadReport} disabled={downloading} className="btn-primary">
          <Download size={16} />
          {downloading ? 'Preparing PDF...' : 'Download PDF Report'}
        </button>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="glass-card flex items-center justify-center p-6">
          <ScoreGauge score={analysis.ats_score} />
        </div>
        <div className="glass-card p-6 lg:col-span-2">
          <h3 className="mb-2 font-semibold">Score Breakdown</h3>
          <ScoreBreakdownChart analysis={analysis} />
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="glass-card p-6">
          <h3 className="mb-3 font-semibold">Matched Skills</h3>
          <SkillBadgeList skills={analysis.matched_skills} variant="matched" />
        </div>
        <div className="glass-card p-6">
          <h3 className="mb-3 font-semibold">Missing Skills</h3>
          <SkillBadgeList skills={analysis.missing_skills} variant="missing" />
        </div>
      </div>

      <div className="mb-6 grid grid-cols-1 gap-6 md:grid-cols-2">
        <ListCard icon={ThumbsUp} title="Strengths" items={analysis.strengths} tone="text-green-500" />
        <ListCard icon={ThumbsDown} title="Weaknesses" items={analysis.weaknesses} tone="text-red-500" />
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <ListCard icon={Lightbulb} title="Improvement Suggestions" items={analysis.suggestions} tone="text-amber-500" />
        <ListCard
          icon={GraduationCap}
          title="Recommended Certifications"
          items={analysis.recommended_certifications.length ? analysis.recommended_certifications : ['No specific certifications recommended for this match.']}
          tone="text-brand-600"
        />
      </div>
    </Layout>
  )
}
