import { Check, X } from 'lucide-react'

export function SkillBadgeList({ skills, variant = 'matched' }) {
  const isMatched = variant === 'matched'
  if (!skills?.length) {
    return <p className="text-sm text-gray-400">None found.</p>
  }
  return (
    <div className="flex flex-wrap gap-2">
      {skills.map((skill) => (
        <span
          key={skill}
          className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ${
            isMatched
              ? 'bg-green-50 text-green-700 dark:bg-green-500/10 dark:text-green-400'
              : 'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400'
          }`}
        >
          {isMatched ? <Check size={12} /> : <X size={12} />}
          {skill}
        </span>
      ))}
    </div>
  )
}
