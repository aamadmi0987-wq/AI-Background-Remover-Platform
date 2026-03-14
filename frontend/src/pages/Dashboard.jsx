import { useEffect, useMemo, useState } from 'react'
import { AuthCard } from '../components/AuthCard'
import { UploadCard } from '../components/UploadCard'
import { authStore } from '../api/client'
import { JobStatusCard } from '../components/JobStatusCard'
import { HistoryCard } from '../components/HistoryCard'

export default function Dashboard() {
  const [token, setToken] = useState(authStore.getToken())
  const [latestJobId, setLatestJobId] = useState(null)
  const isAuthenticated = useMemo(() => !!token, [token])

  useEffect(() => {
    const onExpired = () => {
      setToken('')
      setLatestJobId(null)
    }
    window.addEventListener('auth:expired', onExpired)
    return () => window.removeEventListener('auth:expired', onExpired)
  }, [])

  return (
    <main className="max-w-5xl mx-auto py-10 px-4 space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">AI Background Remover Platform</h1>
          <p className="text-sm text-slate-300 mt-1">Secure login, async processing, and downloadable background-free images.</p>
        </div>
        {isAuthenticated && (
          <button
            className="rounded bg-slate-700 px-3 py-2 text-sm"
            onClick={() => {
              authStore.clearToken()
              setToken('')
              setLatestJobId(null)
            }}
          >
            Logout
          </button>
        )}
      </div>

      {!isAuthenticated ? (
        <AuthCard onAuthenticated={(t) => setToken(t)} />
      ) : (
        <div className="grid md:grid-cols-2 gap-6">
          <UploadCard onJobCreated={(jobId) => setLatestJobId(jobId)} />
          <JobStatusCard jobId={latestJobId} />
          <div className="md:col-span-2">
            <HistoryCard />
          </div>
        </div>
      )}
    </main>
  )
}
