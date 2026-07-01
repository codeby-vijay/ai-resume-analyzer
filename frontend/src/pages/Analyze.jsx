import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { UploadCloud, FileText, Loader2 } from 'lucide-react'
import Layout from '../components/Layout'
import api from '../api/client'

export default function Analyze() {
  const navigate = useNavigate()
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const [jdTitle, setJdTitle] = useState('')
  const [jdText, setJdText] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const handleFileSelect = (selected) => {
    if (!selected) return
    const ext = selected.name.split('.').pop().toLowerCase()
    if (!['pdf', 'docx'].includes(ext)) {
      toast.error('Only PDF and DOCX files are supported.')
      return
    }
    if (selected.size > 5 * 1024 * 1024) {
      toast.error('File must be under 5MB.')
      return
    }
    setFile(selected)
  }

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragOver(false)
    handleFileSelect(e.dataTransfer.files?.[0])
  }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      toast.error('Please upload a resume file.')
      return
    }
    if (jdText.trim().length < 30) {
      toast.error('Job description must be at least 30 characters.')
      return
    }

    setSubmitting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data: resume } = await api.post('/resumes/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })

      const { data: jd } = await api.post('/job-descriptions', {
        title: jdTitle || null,
        raw_text: jdText,
      })

      const { data: analysis } = await api.post('/analyze', {
        resume_id: resume.id,
        job_description_id: jd.id,
      })

      toast.success('Analysis complete!')
      navigate(`/analysis/${analysis.id}`)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Something went wrong during analysis.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Layout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold">New ATS Analysis</h1>
        <p className="text-gray-500 dark:text-gray-400">
          Upload your resume and paste a job description to get your compatibility score.
        </p>
      </div>

      <form onSubmit={onSubmit} className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="glass-card p-6">
          <h2 className="mb-4 font-semibold">1. Upload Resume</h2>
          <label
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={`flex h-56 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed transition ${
              dragOver ? 'border-brand-500 bg-brand-50 dark:bg-brand-500/10' : 'border-gray-200 dark:border-gray-700'
            }`}
          >
            <input
              type="file"
              accept=".pdf,.docx"
              className="hidden"
              onChange={(e) => handleFileSelect(e.target.files?.[0])}
            />
            {file ? (
              <>
                <FileText size={36} className="mb-2 text-brand-600" />
                <p className="font-medium">{file.name}</p>
                <p className="text-xs text-gray-400">{(file.size / 1024).toFixed(0)} KB &middot; click to replace</p>
              </>
            ) : (
              <>
                <UploadCloud size={36} className="mb-2 text-gray-400" />
                <p className="font-medium">Drag & drop or click to upload</p>
                <p className="text-xs text-gray-400">PDF or DOCX, max 5MB</p>
              </>
            )}
          </label>
        </div>

        <div className="glass-card p-6">
          <h2 className="mb-4 font-semibold">2. Job Description</h2>
          <input
            className="input-field mb-3"
            placeholder="Job title (optional) — e.g. Senior Backend Engineer"
            value={jdTitle}
            onChange={(e) => setJdTitle(e.target.value)}
          />
          <textarea
            className="input-field h-40 resize-none"
            placeholder="Paste the full job description here..."
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
          />
          <p className="mt-1 text-xs text-gray-400">{jdText.length} characters</p>
        </div>

        <div className="lg:col-span-2">
          <button type="submit" disabled={submitting} className="btn-primary w-full py-3 text-base">
            {submitting ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Analyzing your resume...
              </>
            ) : (
              'Run ATS Analysis'
            )}
          </button>
        </div>
      </form>
    </Layout>
  )
}
