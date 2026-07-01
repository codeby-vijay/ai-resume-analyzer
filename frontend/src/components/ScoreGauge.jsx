import { motion } from 'framer-motion'

function scoreColor(score) {
  if (score >= 75) return '#16a34a'
  if (score >= 50) return '#ca8a04'
  return '#dc2626'
}

export default function ScoreGauge({ score, size = 160, label = 'ATS Score' }) {
  const radius = (size - 20) / 2
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (Math.min(Math.max(score, 0), 100) / 100) * circumference
  const color = scoreColor(score)

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="currentColor"
          strokeWidth={12}
          fill="none"
          className="text-gray-100 dark:text-gray-800"
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={12}
          fill="none"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
      </svg>
      <div className="-mt-24 flex flex-col items-center">
        <span className="text-4xl font-bold" style={{ color }}>
          {Math.round(score)}
        </span>
        <span className="text-xs text-gray-500 dark:text-gray-400">/ 100</span>
      </div>
      <p className="mt-2 text-sm font-medium text-gray-600 dark:text-gray-300">{label}</p>
    </div>
  )
}
