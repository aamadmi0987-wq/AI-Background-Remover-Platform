import { useState } from 'react'
import { api, authStore } from '../api/client'

export function AuthCard({ onAuthenticated }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('user@example.com')
  const [password, setPassword] = useState('StrongPassword123!')
  const [verificationToken, setVerificationToken] = useState('')
  const [verificationUrl, setVerificationUrl] = useState('')
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const safeError = (e) => e?.response?.data?.detail || 'Request failed'

  const handleSignup = async () => {
    setLoading(true)
    setError('')
    setStatus('')
    try {
      const response = await api.post('/auth/signup', {
        email,
        password,
        captcha_token: 'dev-pass',
      })
      const url = response.data.verification_url
      setVerificationUrl(url)
      setVerificationToken(url?.split('token=')?.[1] || '')
      setStatus('Signup successful. Verify email, then login.')
    } catch (e) {
      setError(safeError(e))
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async () => {
    setLoading(true)
    setError('')
    setStatus('')
    try {
      await api.post('/auth/verify-email', { token: verificationToken })
      setStatus('Email verified. Switch to login.')
      setMode('login')
    } catch (e) {
      setError(safeError(e))
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async () => {
    setLoading(true)
    setError('')
    setStatus('')
    try {
      const response = await api.post('/auth/login', { email, password })
      authStore.setToken(response.data.access_token)
      onAuthenticated(response.data.access_token)
    } catch (e) {
      setError(safeError(e))
    } finally {
      setLoading(false)
    }
  }

  const canSubmit = email.includes('@') && password.length >= 8 && !loading

  return (
    <div className="rounded-xl bg-slate-900 p-6 shadow-lg space-y-4">
      <div className="flex items-center justify-between gap-3">
        <h2 className="text-xl font-semibold">Account Access</h2>
        <div className="rounded-lg bg-slate-800 p-1 text-sm">
          <button
            className={`px-3 py-1 rounded ${mode === 'login' ? 'bg-emerald-500 text-black' : 'text-slate-200'}`}
            onClick={() => setMode('login')}
          >
            Login
          </button>
          <button
            className={`px-3 py-1 rounded ${mode === 'signup' ? 'bg-emerald-500 text-black' : 'text-slate-200'}`}
            onClick={() => setMode('signup')}
          >
            Signup
          </button>
        </div>
      </div>

      <div className="grid gap-3">
        <input className="w-full rounded bg-slate-800 px-3 py-2" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input className="w-full rounded bg-slate-800 px-3 py-2" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password (min 8 chars)" />
      </div>

      {mode === 'login' ? (
        <button disabled={!canSubmit} onClick={handleLogin} className="rounded bg-emerald-500 px-4 py-2 text-black font-medium disabled:opacity-50">
          {loading ? 'Logging in...' : 'Login'}
        </button>
      ) : (
        <div className="space-y-3">
          <button disabled={!canSubmit} onClick={handleSignup} className="rounded bg-emerald-500 px-4 py-2 text-black font-medium disabled:opacity-50">
            {loading ? 'Creating...' : 'Create account'}
          </button>

          {verificationUrl && (
            <div className="space-y-2 text-sm rounded-lg bg-slate-800 p-3">
              <p className="text-slate-300">Verification URL (dev mode)</p>
              <p className="text-emerald-300 break-all">{verificationUrl}</p>
              <input
                className="w-full rounded bg-slate-700 px-3 py-2"
                value={verificationToken}
                onChange={(e) => setVerificationToken(e.target.value)}
                placeholder="Verification token"
              />
              <button disabled={loading || !verificationToken} onClick={handleVerify} className="rounded bg-indigo-500 px-4 py-2 text-white disabled:opacity-50">
                Verify Email
              </button>
            </div>
          )}
        </div>
      )}

      {status && <p className="text-sm text-emerald-300">{status}</p>}
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  )
}
