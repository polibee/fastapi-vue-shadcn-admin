import { beforeEach, describe, expect, it, vi } from 'vitest'

const { settingsRequest, setConfig } = vi.hoisted(() => ({ settingsRequest: vi.fn(), setConfig: vi.fn() }))

vi.mock('./generated/client', () => ({ readSettingsApiV1SettingsGet: settingsRequest }))
vi.mock('./generated/client/client.gen', () => ({ client: { setConfig } }))

import { fetchSettings } from './settings'

describe('settings API adapter', () => {
  beforeEach(() => {
    settingsRequest.mockReset()
    setConfig.mockReset()
  })

  it('reads the direct safe settings response from the generated SDK', async () => {
    settingsRequest.mockResolvedValue({
      app_name: 'Admin',
      environment: 'test',
      api_docs_enabled: false,
      jwt_access_token_minutes: 45,
      task_lease_seconds: 120,
      database_configured: true,
      redis_configured: false,
    })

    await expect(fetchSettings()).resolves.toEqual({
      app_name: 'Admin',
      environment: 'test',
      api_docs_enabled: false,
      jwt_access_token_minutes: 45,
      task_lease_seconds: 120,
      database_configured: true,
      redis_configured: false,
    })
  })
})
