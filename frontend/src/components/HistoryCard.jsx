import { useEffect, useState } from 'react'
import { api } from '../api/client'

export function HistoryCard() {
  const [items, setItems] = useState([])
  const [error, setError] = useState('')

  const load = async () => {
    try {
      const response = await api.get('/images/history')
      setItems(response.data)
      setError('')
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load history')
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div className="rounded-xl bg-slate-900 p-6 shadow-lg space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Upload History</h3>
        <button className="rounded bg-slate-700 px-3 py-1 text-xs" onClick={load}>Refresh</button>
      </div>
      {error && <p className="text-sm text-red-400">{error}</p>}
      {items.length === 0 ? (
        <p className="text-sm text-slate-300">No images uploaded yet.</p>
      ) : (
        <ul className="space-y-2 text-sm">
          {items.slice(0, 10).map((item) => (
            <li key={item.id} className="rounded bg-slate-800 p-2">
              <a href={item.image_url} target="_blank" rel="noreferrer" className="text-indigo-300 underline break-all">
                {item.image_url}
              </a>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
