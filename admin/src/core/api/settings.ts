import { readSettingsApiV1SettingsGet } from './generated/client'
import { client } from './generated/client/client.gen'
import { getAccessToken } from './auth'
import type { SettingsRead } from './generated/client'

export type RuntimeSettings = SettingsRead

export async function fetchSettings(): Promise<RuntimeSettings> {
  client.setConfig({ baseUrl: '' })
  const result = await readSettingsApiV1SettingsGet({
    auth: getAccessToken() ?? undefined,
    responseStyle: 'data',
    throwOnError: true,
  })
  return result as unknown as RuntimeSettings
}
