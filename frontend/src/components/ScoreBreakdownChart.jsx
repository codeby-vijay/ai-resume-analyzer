import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, CartesianGrid } from 'recharts'

const COLORS = ['#4f46e5', '#7c3aed', '#db2777', '#0ea5e9', '#16a34a']

export default function ScoreBreakdownChart({ analysis }) {
  const data = [
    { name: 'Skill Match', value: analysis.skill_match_score },
    { name: 'Experience', value: analysis.experience_match_score },
    { name: 'Education', value: analysis.education_match_score },
    { name: 'Keyword Density', value: analysis.keyword_density_score },
    { name: 'Formatting', value: analysis.formatting_score },
  ]

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-gray-200 dark:stroke-gray-800" />
        <XAxis dataKey="name" tick={{ fontSize: 12 }} interval={0} angle={-15} textAnchor="end" height={60} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{ borderRadius: 12, border: 'none', boxShadow: '0 4px 20px rgba(0,0,0,0.1)' }}
          formatter={(value) => [`${value.toFixed(0)}/100`, 'Score']}
        />
        <Bar dataKey="value" radius={[8, 8, 0, 0]}>
          {data.map((_, index) => (
            <Cell key={index} fill={COLORS[index % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
