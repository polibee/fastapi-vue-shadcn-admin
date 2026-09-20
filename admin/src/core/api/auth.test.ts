import { beforeEach, describe, expect, it } from 'vitest'
import { ApiError, clearAccessToken, getAccessToken, setAccessToken, withBearer } from './auth'

describe('auth token storage', () => {
  beforeEach(() => clearAccessToken())

  it('stores and clears the access token and adds a bearer header', () => {
    setAccessToken('token-123')
    expect(getAccessToken()).toBe('token-123')
    expect(withBearer({ Accept: 'application/json' })).toEqual({
      Accept: 'application/json',
      Authorization: 'Bearer token-123',
    })

    clearAccessToken()
    expect(getAccessToken()).toBeNull()
    expect(withBearer()).toEqual({})
  })

  it('preserves the API error code for localized UI messages', () => {
    const error = new ApiError('invalid_credentials', '用户名或密码错误。')
    expect(error.code).toBe('invalid_credentials')
    expect(error.message).toBe('用户名或密码错误。')
  })
})
