import { apiErrorMessage, networkErrorMessage } from './i18n/apiError'

export const API_URL = 'http://localhost:8000'

export const getToken = () => localStorage.getItem('token')
export const setToken = (token) => localStorage.setItem('token', token)
export const clearToken = () => localStorage.removeItem('token')

export function getRole() {
  const token = getToken()
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
    return payload.role ?? null
  } catch {
    return null
  }
}

/** Error from the API. `message` is already translated; `code` is the API's stable code. */
export class ApiError extends Error {
  constructor(message, status, code) {
    super(message)
    this.status = status
    this.code = code
  }
}

export async function apiRequest(path, { auth = false, body, method = 'GET' } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (auth) headers.Authorization = `Bearer ${getToken()}`

  let res
  try {
    res = await fetch(`${API_URL}${path}`, {
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers,
      method,
    })
  } catch {
    throw new ApiError(networkErrorMessage(), 0, 'NETWORK_ERROR')
  }

  let result = null
  if (res.status !== 204) {
    const data = await res.json().catch(() => null)
    if (!res.ok) throw new ApiError(apiErrorMessage(data), res.status, data?.code)
    result = data
  }
  return result
}
