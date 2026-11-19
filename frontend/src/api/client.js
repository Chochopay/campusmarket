const TOKEN_KEY = 'token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token)
export const clearToken = () => localStorage.removeItem(TOKEN_KEY)

let onUnauthorized = () => {}
export const setUnauthorizedHandler = (fn) => { onUnauthorized = fn }

export class ApiError extends Error {
  constructor(status, message, fieldErrors = {}) {
    super(message)
    this.status = status
    this.fieldErrors = fieldErrors
  }
}

// FastAPI отдаёт detail строкой (HTTPException) или массивом {loc, msg} (422)
function translate(item) {
  const ctx = item.ctx || {}
  switch (item.type) {
    case 'missing': return 'Обязательное поле'
    case 'string_too_short': return `Слишком короткое значение (минимум ${ctx.min_length})`
    case 'string_too_long': return `Слишком длинное значение (максимум ${ctx.max_length})`
    case 'int_parsing':
    case 'int_type':
    case 'decimal_parsing':
    case 'decimal_type': return 'Введите число'
    case 'literal_error': return 'Недопустимое значение'
    case 'value_error': return String(item.msg).replace(/^Value error, /, '')
    default: return item.msg
  }
}

// FastAPI отдаёт detail строкой (HTTPException) или массивом {loc, type, msg} (422)
function parseError(status, data) {
  const detail = data?.detail
  if (typeof detail === 'string') return new ApiError(status, detail)
  if (Array.isArray(detail)) {
    const fieldErrors = {}
    const general = []
    for (const item of detail) {
      const field = item.loc?.[item.loc.length - 1]
      const message = translate(item)
      if (typeof field === 'string' && field !== 'body') fieldErrors[field] = message
      else general.push(message)
    }
    return new ApiError(status, general.join('; ') || 'Проверьте введённые данные', fieldErrors)
  }
  return new ApiError(status, 'Что-то пошло не так. Попробуйте позже.')
}

async function request(method, path, body) {
  const headers = {}
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const options = { method, headers }
  if (body instanceof FormData) {
    options.body = body // Content-Type с границей поставит сам браузер
  } else if (body !== undefined) {
    headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }

  let response
  try {
    response = await fetch(`/api${path}`, options)
  } catch {
    throw new ApiError(0, 'Нет связи с сервером. Проверьте подключение.')
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    if (response.status === 401 && token) onUnauthorized()
    throw parseError(response.status, data)
  }
  return data
}

export const api = {
  get: (path) => request('GET', path),
  post: (path, body) => request('POST', path, body),
  patch: (path, body) => request('PATCH', path, body),
  delete: (path) => request('DELETE', path),
}

// ?a=1&b=2 из объекта, пустые значения пропускаются
export function withQuery(path, params = {}) {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') search.set(key, value)
  }
  const qs = search.toString()
  return qs ? `${path}?${qs}` : path
}