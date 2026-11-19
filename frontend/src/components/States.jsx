export function Loading() {
  return <p className="p-4 text-gray-500">Загрузка…</p>
}

export function ErrorBox({ error, onRetry }) {
  return (
    <div className="rounded bg-red-50 p-4 text-red-800">
      <p>{error.message}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-2 rounded border border-red-300 px-3 py-1">
          Повторить
        </button>
      )}
    </div>
  )
}

export function Empty({ children }) {
  return <div className="rounded bg-white p-6 text-center text-gray-600 shadow">{children}</div>
}