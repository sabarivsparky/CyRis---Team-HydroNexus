/**
 * REAL LOGIC — Frontend API Client.
 * Handles typed HTTP requests to the CyRIS FastAPI backend with uniform error handling.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export interface ApiErrorPayload {
  error: {
    code: string
    message: string
    details?: unknown[]
  }
}

export class ApiError extends Error {
  code: string
  details?: unknown[]

  constructor(code: string, message: string, details?: unknown[]) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.details = details
  }
}

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), 10000)

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...(options?.headers || {}),
      },
    })

    if (!res.ok) {
      let errPayload: ApiErrorPayload | null = null
      try {
        errPayload = await res.json()
      } catch {
        // fallback if non-JSON
      }

      const code = errPayload?.error?.code || `http_${res.status}`
      const msg = errPayload?.error?.message || `HTTP ${res.status} Error`
      throw new ApiError(code, msg, errPayload?.error?.details)
    }

    return (await res.json()) as T
  } catch (err: unknown) {
    if (err instanceof ApiError) {
      throw err
    }
    if ((err as Error).name === 'AbortError') {
      throw new ApiError('timeout', 'API request timed out after 10s')
    }
    throw new ApiError('network_error', (err as Error).message || 'Network request failed')
  } finally {
    clearTimeout(timeoutId)
  }
}
