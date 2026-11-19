import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const inputClass = 'w-full rounded border px-3 py-2'

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-sm space-y-3 rounded bg-white p-4 shadow">
      <h1 className="text-xl font-bold">Вход</h1>
      <input className={inputClass} placeholder="Логин" value={username}
             onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
      <input className={inputClass} type="password" placeholder="Пароль" value={password}
             onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button type="submit" disabled={submitting}
              className="w-full rounded bg-blue-600 px-3 py-2 text-white disabled:opacity-50">
        {submitting ? 'Входим…' : 'Войти'}
      </button>
      <p className="text-sm text-gray-600">
        Нет аккаунта? <Link to="/register" className="text-blue-600">Регистрация</Link>
      </p>
    </form>
  )
}