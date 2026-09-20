import { listPermissionsApiV1PermissionsGet, type PermissionRead } from './generated/client'
import { client } from './generated/client/client.gen'
import { getAccessToken } from './auth'

export async function loadPermissions(): Promise<{ items: PermissionRead[]; total: number }> {
  client.setConfig({ baseUrl: '' })
  const result = await listPermissionsApiV1PermissionsGet({ auth: getAccessToken() ?? undefined, responseStyle: 'data', throwOnError: true })
  return result as unknown as { items: PermissionRead[]; total: number }
}
