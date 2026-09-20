import { beforeEach, describe, expect, it, vi } from 'vitest'

const { loginRequest, refreshRequest, revokeRequest, setConfig } = vi.hoisted(() => ({ loginRequest: vi.fn(), refreshRequest: vi.fn(), revokeRequest: vi.fn(), setConfig: vi.fn() }))

vi.mock('./generated/client', () => ({
  loginApiV1AuthLoginPost: loginRequest,
  refreshApiV1AuthRefreshPost: refreshRequest,
  revokeApiV1AuthRevokePost: revokeRequest,
  currentUserApiV1AuthMeGet: vi.fn(),
}))
vi.mock('./generated/client/client.gen', () => ({ client: { setConfig } }))

import { clearAccessToken, getAccessToken, login, refreshAccessToken, revokeRefreshToken } from './auth'

describe('generated SDK login adapter', () => {
  beforeEach(() => {
    clearAccessToken()
    loginRequest.mockReset()
    refreshRequest.mockReset()
    revokeRequest.mockReset()
    setConfig.mockReset()
  })

  it('reads the direct business response returned by responseStyle data', async () => {
    loginRequest.mockResolvedValue({ access_token: 'token-456', refresh_token: 'refresh-456', token_type: 'bearer' })

    const result = await login({ username: 'admin', password: 'secret' })

    expect(result.access_token).toBe('token-456')
    expect(getAccessToken()).toBe('token-456')
  })

  it('rotates the access and refresh tokens', async () => {
    loginRequest.mockResolvedValue({ access_token: 'token-456', refresh_token: 'refresh-456', token_type: 'bearer' })
    refreshRequest.mockResolvedValue({ access_token: 'token-789', refresh_token: 'refresh-789', token_type: 'bearer' })

    await login({ username: 'admin', password: 'secret' })
    const result = await refreshAccessToken()

    expect(result.access_token).toBe('token-789')
    expect(getAccessToken()).toBe('token-789')
  })

  it('revokes the stored refresh token on sign out', async () => {
    loginRequest.mockResolvedValue({ access_token: 'token-456', refresh_token: 'refresh-456', token_type: 'bearer' })
    revokeRequest.mockResolvedValue(undefined)

    await login({ username: 'admin', password: 'secret' })
    await revokeRefreshToken()

    expect(revokeRequest).toHaveBeenCalledWith(expect.objectContaining({ body: { refresh_token: 'refresh-456' } }))
    expect(getAccessToken()).toBeNull()
  })
})
