import { useCallback, useEffect, useState } from 'react'
import { api } from '../api/client'

// Загружает path (GET). При смене path загружает заново; reload() повторяет запрос.
export function useApi(path) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)
  const [version, setVersion] = useState(0)

  useEffect(() => {
    let cancelled = false // защита от устаревшего ответа
    setLoading(true)
    setError(null)
    setData(null)
    api.get(path)
      .then((result) => { if (!cancelled) setData(result) })
      .catch((err) => { if (!cancelled) setError(err) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [path, version])

  const reload = useCallback(() => setVersion((v) => v + 1), [])
  return { data, error, loading, reload }
}