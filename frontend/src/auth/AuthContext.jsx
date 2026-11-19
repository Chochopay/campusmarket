import { createContext, useCallback, useEffect, useMemo, useState } from 'react'
import { api, clearToken, getToken, setToken, setUnauthorizedHandler } from '../api/client'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(Boolean(getToken()))

  const logout = useCallback(() => {
    clearToken()
    setUser(null)
  }, [])

  // при старте: если токен сохранён, узнаём, чей он
  useEffect(() => {
    setUnauthorizedHandler(logout)
    if (!getToken()) return
    api.get('/users/me')
      .then(setUser)
      .catch(() => clearToken())
      .finally(() => setLoading(false))
  }, [logout])

  const login = useCallback(async (username, password) => {
    const { jwt_token } = await api.post('/auth/login', { username, password })
    setToken(jwt_token)
    setUser(await api.get('/users/me'))
  }, [])

  const register = useCallback(async (username, password) => {
    await api.post('/auth/register', { username, password })
    await login(username, password)
  }, [login])

  const value = useMemo(
    () => ({ user, loading, login, register, logout }),
    [user, loading, login, register, logout],
  )
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}