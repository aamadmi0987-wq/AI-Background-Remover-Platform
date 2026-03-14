import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function JobStatusCard({ jobId }) {
  const [job, setJob] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!jobId) return
    let timer
    let active = true

    const poll = async () => {
      try {
        const response = await api.get(`/jobs/${jobId}`)
        if (!active) return
        setJob(response.data)
        setError('')
        if (['queued', 'processing'].includes(response.data.status)) {
          timer = setTimeout(poll, 2000)
        }
      } catch (e) {
        if (!active) return
        setError(e?.response?.data?.detail || 'Could not load job status')
      }
    }

    poll()
    return () => {
      active = false
      if (timer) clearTimeout(timer)
    }
  }, [jobId])

  if (!jobId) {
    return (
      <div className="rounded-xl bg-slate-900 p-6 shadow-lg text-sm text-slate-300">
        No active job yet. Start by uploading an image.
      </div>
    )
  }

  return (
    <div className="rounded-xl bg-slate-900 p-6 shadow-lg space-y-2">
      <h3 className="text-lg font-semibold">Latest Job Status</h3>
      <p className="text-sm">Job ID: {jobId}</p>
      {job && <p className="text-sm">Status: <span className="text-emerald-300">{job.status}</span></p>}
      {job?.output_image_url && (
        <a className="text-sm text-indigo-300 underline" href={job.output_image_url} target="_blank" rel="noreferrer">
          Download processed image
        </a>
      )}
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  )
}
