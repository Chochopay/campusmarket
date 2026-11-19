export default function Pagination({ total, limit, page, onPage }) {
  const pages = Math.max(1, Math.ceil(total / limit))
  if (pages <= 1) return null

  const buttonClass = 'rounded border border-gray-300 bg-white px-3 py-1 disabled:opacity-40'
  return (
    <div className="flex items-center justify-center gap-3">
      <button className={buttonClass} disabled={page <= 1} onClick={() => onPage(page - 1)}>Назад</button>
      <span className="text-sm text-gray-600">Страница {page} из {pages}</span>
      <button className={buttonClass} disabled={page >= pages} onClick={() => onPage(page + 1)}>Вперёд</button>
    </div>
  )
}