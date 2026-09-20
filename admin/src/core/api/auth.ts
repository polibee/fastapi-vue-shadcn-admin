import { currentUserApiV1AuthMeGet, loginApiV1AuthLoginPost, refreshApiV1AuthRefreshPost, revokeApiV1AuthRevokePost } from './generated/client'
import { client } from './generated/client/client.gen'

const ACCESS_TOKEN_KEY = 'admin-access-token'
const REFRESH_TOKEN_KEY = 'admin-refresh-token'
let memoryToken: string | null = null
let memoryRefreshToken: string | null = null

export const demoCredentials = { username: 'integration-admin', password: 'integration-password' } as const

export class ApiError extends Error {
  constructor(public readonly code: string, message: string) {
    super(message)
    this.name = 'ApiError'
  }
}

function storage(): Storage | null {
  return typeof window === 'undefined' ? null : window.localStorage
}

export function getAccessToken(): string | null {
  return storage()?.getItem(ACCESS_TOKEN_KEY) ?? memoryToken
}

export function getRefreshToken(): string | null {
  return storage()?.getItem(REFRESH_TOKEN_KEY) ?? memoryRefreshToken
}

export function setAccessToken(token: string): void {
  memoryToken = token
  storage()?.setItem(ACCESS_TOKEN_KEY, token)
}

export function setRefreshToken(token: string): void {
  memoryRefreshToken = token
  storage()?.setItem(REFRESH_TOKEN_KEY, token)
}

export function clearAccessToken(): void {
  memoryToken = null
  memoryRefreshToken = null
  storage()?.removeItem(ACCESS_TOKEN_KEY)
  storage()?.removeItem(REFRESH_TOKEN_KEY)
}

export function withBearer(headers: HeadersInit = {}): HeadersInit {
  const token = getAccessToken()
  return token ? { ...headers, Authorization: `Bearer ${token}` } : headers
}

export type LoginPayload = { username: string; password: string }
export type LoginResponse = { access_token: string; refresh_token?: string; token_type: string }
export type CurrentUser = { id: number; username: string; email: string; is_active: boolean; permissions: string[] }

export async function login(payload: LoginPayload): Promise<LoginResponse> {
  client.setConfig({ baseUrl: '' })
  let result: LoginResponse
  try {
    const response = await loginApiV1AuthLoginPost({ body: payload, responseStyle: 'data', throwOnError: true })
    result = response as unknown as LoginResponse
  } catch (error) {
    throw toApiError(error)
  }
  setAccessToken(result.access_token)
  if (result.refresh_token) setRefreshToken(result.refresh_token)
  client.setConfig({ headers: withBearer() })
  return result
}

export async function refreshAccessToken(): Promise<LoginResponse> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) throw new ApiError('invalid_refresh_token', 'No refresh token is available.')
  try {
    const response = await refreshApiV1AuthRefreshPost({ body: { refresh_token: refreshToken }, responseStyle: 'data', throwOnError: true })
    const result = response as unknown as LoginResponse
    setAccessToken(result.access_token)
    if (result.refresh_token) setRefreshToken(result.refresh_token)
    client.setConfig({ headers: withBearer() })
    return result
  } catch (error) {
    clearAccessToken()
    throw toApiError(error)
  }
}

export async function revokeRefreshToken(): Promise<void> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) {
    clearAccessToken()
    return
  }
  try {
    await revokeApiV1AuthRevokePost({ body: { refresh_token: refreshToken }, responseStyle: 'data', throwOnError: true })
  } finally {
    clearAccessToken()
  }
}

export async function fetchCurrentUser(): Promise<CurrentUser> {
  client.setConfig({ baseUrl: '' })
  try {
    const response = await currentUserApiV1AuthMeGet({ auth: getAccessToken() ?? undefined, responseStyle: 'data', throwOnError: true })
    return response as unknown as CurrentUser
  } catch (error) {
    throw toApiError(error)
  }
}

function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error
  const payload = (error as { message?: string; data?: { message?: string; code?: string } })
  return new ApiError(payload.data?.code ?? 'request_failed', payload.data?.message ?? payload.message ?? 'request_failed')
}
