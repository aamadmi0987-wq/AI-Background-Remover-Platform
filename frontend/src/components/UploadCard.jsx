import { useState } from 'react'
import { api } from '../api/client'

export function UploadCard({ onJobCreated }) {
  const [file, setFile] = useState(null)
  const [job, setJob] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const onUpload = async () => {
    try {
      setError('')
      if (!file) {
        setError('Please choose an image first')
        return
      }
      setBusy(true)
      const form = new FormData()
      form.append('file', file)
      const upload = await api.post('/images/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const queued = await api.post('/jobs/remove-background', null, {
        params: { image_url: upload.data.image_url },
      })
      setJob(queued.data)
      onJobCreated?.(queued.data.job_id)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Upload failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="rounded-xl bg-slate-900 p-6 shadow-lg space-y-4">
      <h2 className="text-xl font-semibold">Upload an image</h2>
      <input type="file" accept="image/*" className="block w-full" onChange={(e) => setFile(e.target.files?.[0])} />
      <button disabled={busy} onClick={onUpload} className="rounded bg-emerald-500 px-4 py-2 text-black font-medium disabled:opacity-50">
        {busy ? 'Uploading...' : 'Start Background Removal'}
      </button>
      {job && <p className="text-sm">Queued job #{job.job_id} ({job.status})</p>}
      {error && <p className="text-sm text-red-400">{error}</p>}
    </div>
  )
}
