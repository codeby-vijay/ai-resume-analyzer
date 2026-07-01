import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { FileScan } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export default function Register() {
  const { register: registerUser } = useAuth()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)
  const { register, handleSubmit, watch, formState: { errors } } = useForm()

  const onSubmit = async (values) => {
    setSubmitting(true)
    try {
      await registerUser(values.full_name, values.email, values.password)
      toast.success('Account created! Welcome to ResumeAI.')
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-950 dark:to-gray-900 px-4">
      <div className="glass-card w-full max-w-md p-8">
        <div className="mb-8 flex flex-col items-center">
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-gradient text-white">
            <FileScan size={22} />
          </div>
          <h1 className="text-2xl font-bold">Create your account</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Start optimizing your resume for ATS in seconds</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Full Name</label>
            <input
              className="input-field"
              placeholder="Jane Smith"
              {...register('full_name', { required: 'Name is required', minLength: { value: 2, message: 'Too short' } })}
            />
            {errors.full_name && <p className="mt-1 text-xs text-red-500">{errors.full_name.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <input
              type="email"
              className="input-field"
              placeholder="you@example.com"
              {...register('email', { required: 'Email is required' })}
            />
            {errors.email && <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="At least 8 characters"
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 8, message: 'Minimum 8 characters' },
              })}
            />
            {errors.password && <p className="mt-1 text-xs text-red-500">{errors.password.message}</p>}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">Confirm Password</label>
            <input
              type="password"
              className="input-field"
              placeholder="Re-enter your password"
              {...register('confirm_password', {
                required: 'Please confirm your password',
                validate: (value) => value === watch('password') || 'Passwords do not match',
              })}
            />
            {errors.confirm_password && (
              <p className="mt-1 text-xs text-red-500">{errors.confirm_password.message}</p>
            )}
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-brand-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  )
}
