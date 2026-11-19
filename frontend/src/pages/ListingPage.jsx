import { useState } from 'react'
import { Link, useParams } from 'react-router'
import { api } from '../api/client'
import { useApi } from '../hooks/useApi'
import { useAuth } from '../auth/useAuth'
import Badge from '../components/Badge'
import FavoriteButton from '../components/FavoriteButton'
import Gallery from '../components/Gallery'
import TextForm from '../components/TextForm'
import { Empty, ErrorBox, Loading } from '../components/States'
import { formatDate, formatPrice } from '../utils/format'
import { CONDITION_LABELS, MODE_LABELS, STATUS_LABELS, STATUS_STYLES } from '../utils/labels'

export default function ListingPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const { data: listing, error, loading, reload } = useApi(`/listings/${id}`)
  const [actionError, setActionError] = useState('') // хуки идут до любых return

  if (loading) return <Loading />
  if (error?.status === 404 || error?.status === 422) {
    return <Empty>Такого объявления нет. <Link to="/" className="text-blue-600 underline">В каталог</Link></Empty>
  }
  if (error) return <ErrorBox error={error} onRetry={reload} />
  if (!listing) return null

  const isOwner = user?.id === listing.user_id
  const isModerator = user && ['moderator', 'admin'].includes(user.role)
  const created = formatDate(listing.created_at)

  async function restore() {
    setActionError('')
    try {
      await api.post(`/listings/${listing.id}/restore`)
      reload()
    } catch (err) {
      setActionError(err.message)
    }
  }

  return (
    <div className="space-y-4">
      <Link to="/" className="text-sm text-blue-600">← В каталог</Link>

      <div className="grid gap-4 md:grid-cols-2">
        <Gallery images={listing.listing_images} />
        <div className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <Badge className={STATUS_STYLES[listing.status]}>{STATUS_LABELS[listing.status]}</Badge>
            <Badge>{MODE_LABELS[listing.mode]}</Badge>
            <Badge>{CONDITION_LABELS[listing.condition]}</Badge>
          </div>
          <h1 className="break-words text-2xl font-bold">{listing.name}</h1>
          <p className="text-2xl font-semibold text-blue-700">{formatPrice(listing)}</p>
          <p className="whitespace-pre-line break-words text-gray-800">{listing.description}</p>
          <p className="text-sm text-gray-500">
            Категория: {listing.category_name} · Продавец: {listing.seller_username}
            {created && <> · Опубликовано {created}</>}
          </p>
        </div>
      </div>

      <section className="space-y-3">
        {!user && (
          <p className="rounded bg-white p-3 shadow">
            Чтобы подать заявку, добавить в избранное или пожаловаться,{' '}
            <Link to="/login" className="text-blue-600 underline">войдите</Link>.
          </p>
        )}

        {isOwner && (
          <p className="rounded bg-white p-3 shadow">
            Это ваше объявление.{' '}
            <Link to={`/listings/${listing.id}/edit`} className="text-blue-600 underline">Редактировать</Link>
          </p>
        )}

        {user && !isOwner && (
          <>
            <FavoriteButton listingId={listing.id} />
            {listing.status === 'published' ? (
              <div className="space-y-2 rounded bg-white p-3 shadow">
                <h2 className="font-semibold">Подать заявку</h2>
                <TextForm
                  field="text"
                  placeholder="Напишите продавцу: когда и где удобно встретиться"
                  submitLabel="Отправить заявку"
                  onSubmit={(text) => api.post(`/listings/${listing.id}/requests`, { text })}
                  successText={<>Заявка отправлена. Её статус смотрите в разделе{' '}
                    <Link to="/my/requests" className="underline">«Мои заявки»</Link>.</>}
                />
              </div>
            ) : (
              <p className="text-gray-600">Заявки на это объявление сейчас не принимаются.</p>
            )}
            <details className="rounded bg-white p-3 shadow">
              <summary className="cursor-pointer font-semibold">Пожаловаться на объявление</summary>
              <div className="mt-2">
                <TextForm
                  field="reason"
                  placeholder="Опишите, что не так с объявлением"
                  submitLabel="Отправить жалобу"
                  onSubmit={(reason) => api.post('/reports/', { listing_id: listing.id, reason })}
                  successText="Жалоба отправлена. Спасибо!"
                />
              </div>
            </details>
          </>
        )}

        {isModerator && listing.status === 'hidden' && (
          <div className="rounded bg-red-50 p-3">
            <p className="mb-2 text-red-800">Объявление скрыто модератором. Видите его вы, потому что вы модератор.</p>
            <button onClick={restore} className="rounded bg-red-600 px-4 py-2 text-white">Вернуть в каталог</button>
            {actionError && <p className="mt-2 text-sm text-red-700">{actionError}</p>}
          </div>
        )}
      </section>
    </div>
  )
}