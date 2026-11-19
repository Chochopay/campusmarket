import { useState } from 'react'

// field: имя поля в теле запроса, чтобы показать у него ошибку сервера (422)
export default function TextForm({ placeholder, submitLabel, field, onSubmit, successText, maxLength = 500 }) {
  const [text, setText] = useState('')
  const [error, setError] = useState(null)
  const [done, setDone] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setSubmitting(true)
    try {
      await onSubmit(text)
      setDone(true)
    } catch (err) {
      setError(err)
    } finally {
      setSubmitting(false)
    }
  }

  if (done) return <p className="rounded bg-green-50 p-3 text-green-800">{successText}</p>

  const fieldError = error?.fieldErrors?.[field]
  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <textarea
        rows={3}
        maxLength={maxLength}
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded border border-gray-300 px-3 py-2"
      />
      {fieldError && <p className="text-sm text-red-600">{fieldError}</p>}
      {error && !fieldError && <p className="text-sm text-red-600">{error.message}</p>}
      <button type="submit" disabled={submitting}
              className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50">
        {submitting ? 'Отправляем…' : submitLabel}
      </button>
    </form>
  )
}