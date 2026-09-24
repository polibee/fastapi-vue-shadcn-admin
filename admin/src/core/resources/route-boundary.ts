import type { ResourceManifest } from './types'

export function assertResourceRouteBoundary(manifest: Pick<ResourceManifest, 'routes' | 'api'>): void {
  if (!manifest.routes.list.startsWith('/admin/')) throw new Error(`resource UI route must start with /admin/: ${manifest.routes.list}`)
  if (!manifest.api.base.startsWith('/api/v1/')) throw new Error(`resource API base must start with /api/v1/: ${manifest.api.base}`)
}
