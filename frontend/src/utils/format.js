export const TIMEZONE = 'Asia/Bishkek'

// Сервер отдаёт время в UTC без суффикса «Z» (SQLite хранит его без пояса).
// Без «Z» браузер считал бы его местным и показал бы неверный час.
export function parseServerDate(value) {
  if (!value) return null
  const hasZone = /[zZ]$|[+-]\d{2}:?\d{2}$/.test(value)
  return new Date(hasZone ? value : `${value}Z`)
}

export function formatDate(value) {
  const date = parseServerDate(value)
  if (!date) return ''
  return new Intl.DateTimeFormat('ru-RU', {
    dateStyle: 'medium', timeStyle: 'short', timeZone: TIMEZONE,
  }).format(date)
}

// Цена приходит строкой ("450.00") или null (обмен)
export function formatPrice(listing) {
  if (listing.mode === 'exchange') return 'Обмен'
  if (listing.mode === 'free') return 'Даром'
  if (listing.price === null || listing.price === undefined) return 'Цена не указана'
  return `${Number(listing.price).toLocaleString('ru-RU')} сом`
}

// В базе путь хранится как "uploads/x.jpeg", в браузере нужен "/uploads/x.jpeg"
export function imageUrl(path) {
  return path.startsWith('/') ? path : `/${path}`
}