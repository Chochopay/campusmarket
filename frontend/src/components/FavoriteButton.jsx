import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function FavoriteButton({ listingId }) {
  const [isFavorite, setIsFavorite] = useState(null) // null: ещё не знаем
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  // признака «в избранном» в карточке нет, берём список избранного (до 100 записей)
  useEffect(() => {
    api.get('/favorites/?limit=100')
      .then((page) => setIsFavorite(page.items.some((item) => item.id === listingId)))
      .catch(() => setIsFavorite(false))
  }, [listingId])

  async function toggle() {
    setBusy(true)
    setError('')
    try {
      if (isFavorite) {
        await api.delete(`/favorites/${listingId}`)
        setIsFavorite(false)
      } else {
        await api.post('/favorites/', { listing_id: listingId })
        setIsFavorite(true)
      }
    } catch (err) {
      if (err.status === 409) setIsFavorite(true) // уже было добавлено
      else setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <button onClick={toggle} disabled={busy || isFavorite === null}
              className="rounded border border-gray-300 bg-white px-4 py-2 disabled:opacity-50">
        {isFavorite ? '★ Убрать из избранного' : '☆ В избранное'}
      </button>
      {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
    </div>
  )
}