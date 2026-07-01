import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FileScan, Sparkles, Target, BarChart3, ShieldCheck } from 'lucide-react'

const features = [
  { icon: Target, title: 'ATS Compatibility Score', desc: 'Get a precise 0-100 score showing how well your resume matches any job description.' },
  { icon: Sparkles, title: 'AI Skill Matching', desc: 'Semantic analysis surfaces matched and missing skills, not just keyword guesses.' },
  { icon: BarChart3, title: 'Visual Breakdown', desc: 'Interactive charts show skill, experience, education, and keyword scoring.' },
  { icon: ShieldCheck, title: 'Actionable Suggestions', desc: 'Get concrete recommendations and certifications to close the gap.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-950 dark:to-gray-900">
      <header className="mx-auto flex max-w-7xl items-center justify-between p-6">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-gradient text-white">
            <FileScan size={18} />
          </div>
          <span className="text-lg font-bold">ResumeAI</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="btn-secondary">Log In</Link>
          <Link to="/register" className="btn-primary">Get Started</Link>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-20 text-center">
        <motion.h1
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-4xl font-extrabold tracking-tight sm:text-6xl"
        >
          Beat the ATS.
          <span className="block bg-brand-gradient bg-clip-text text-transparent">Land the interview.</span>
        </motion.h1>
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="mx-auto mt-6 max-w-2xl text-lg text-gray-600 dark:text-gray-300"
        >
          Upload your resume, paste any job description, and get an instant AI-powered ATS
          compatibility score with matched skills, gaps, and improvement suggestions.
        </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-8 flex justify-center gap-4"
        >
          <Link to="/register" className="btn-primary px-8 py-3 text-base">Analyze My Resume — Free</Link>
        </motion.div>
      </section>

      <section className="mx-auto grid max-w-6xl grid-cols-1 gap-6 px-6 pb-24 sm:grid-cols-2 lg:grid-cols-4">
        {features.map(({ icon: Icon, title, desc }, i) => (
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.1 }}
            className="glass-card p-6"
          >
            <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-brand-gradient text-white">
              <Icon size={20} />
            </div>
            <h3 className="mb-2 font-semibold">{title}</h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">{desc}</p>
          </motion.div>
        ))}
      </section>
    </div>
  )
}
