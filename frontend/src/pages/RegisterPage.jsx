import { useState } from 'react'
import { Link, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'
import FormField from '../components/FormField'

export default function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    if (password !== confirm) {
      setError({ message: 'Пароли не совпадают', fieldErrors: {} })
      return
    }
    setSubmitting(true)
    try {
      await register(username.trim(), password) // регистрирует и сразу входит
      navigate('/')
    } catch (err) {
      setError(err)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-sm space-y-3 rounded bg-white p-4 shadow">
      <h1 className="text-xl font-bold">Регистрация</h1>
      <FormField label="Логин" value={username} onChange={(e) => setUsername(e.target.value)}
                 placeholder="От 4 до 20 символов" autoComplete="username"
                 error={error?.fieldErrors?.username} />
      <FormField label="Пароль" type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                 placeholder="От 8 до 64 символов" autoComplete="new-password"
                 error={error?.fieldErrors?.password} />
      <FormField label="Повторите пароль" type="password" value={confirm}
                 onChange={(e) => setConfirm(e.target.value)} autoComplete="new-password" />
      {error?.message && <p className="text-sm text-red-600">{error.message}</p>}
      <button type="submit" disabled={submitting}
              className="w-full rounded bg-blue-600 px-3 py-2 text-white disabled:opacity-50">
        {submitting ? 'Создаём…' : 'Зарегистрироваться'}
      </button>
      <p className="text-sm text-gray-600">
        Уже есть аккаунт? <Link to="/login" className="text-blue-600">Войти</Link>
      </p>
    </form>
  )
}