import { buildNavigationRegistry, type NavigationEntry } from '@/core/navigation/registry'
import type { ResourceManifest } from '@/core/resources/types'

export type SearchEntry = NavigationEntry & {
  id: string
  group: 'workspace' | 'manage'
}

function toSearchEntry(entry: NavigationEntry, group: SearchEntry['group']): SearchEntry {
  return { ...entry, id: `navigation:${entry.to}`, group }
}

export function buildSearchRegistry(manifests: ResourceManifest[]): SearchEntry[] {
  const navigation = buildNavigationRegistry(manifests)
  return [
    ...navigation.workspace.map((entry) => toSearchEntry(entry, 'workspace')),
    ...navigation.manage.map((entry) => toSearchEntry(entry, 'manage')),
  ]
}
