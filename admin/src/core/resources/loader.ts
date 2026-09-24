import { getResourceApiV1AdminResourcesNameGet, listResourcesApiV1AdminResourcesGet } from '@/core/api/generated/client'
import { client } from '@/core/api/generated/client/client.gen'
import { getAccessToken } from '@/core/api/auth'
import type { ResourceManifest } from './types'
import { assertResourceRouteBoundary } from './route-boundary'

export async function loadResourceManifest(name: string): Promise<ResourceManifest> {
  client.setConfig({ baseUrl: '' })
  const result = await getResourceApiV1AdminResourcesNameGet({ auth: getAccessToken() ?? undefined, path: { name }, responseStyle: 'data', throwOnError: true })
  const manifest = result as unknown as ResourceManifest
  assertResourceRouteBoundary(manifest)
  return manifest
}

export async function loadResourceIndex(): Promise<ResourceManifest[]> {
  client.setConfig({ baseUrl: '' })
  const result = await listResourcesApiV1AdminResourcesGet({ auth: getAccessToken() ?? undefined, responseStyle: 'data', throwOnError: true })
  const manifests = (((result as unknown) as { items: ResourceManifest[] }).items)
  manifests.forEach(assertResourceRouteBoundary)
  return manifests
}
