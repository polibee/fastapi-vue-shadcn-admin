import type { ResourceManifest } from '@/core/resources/types'
import { adminPath } from '@/router/paths'

export type NavigationIcon = 'activity' | 'dashboard' | 'tasks' | 'users' | 'roles' | 'audit' | 'settings' | 'database' | 'generator' | 'modules' | 'api' | 'permissions'

export type NavigationEntry = {
  to: string
  labelKey: string
  icon: NavigationIcon
  permission?: string
}

export type NavigationRegistry = {
  workspace: NavigationEntry[]
  manage: NavigationEntry[]
}

const staticWorkspace: NavigationEntry[] = [
  { to: adminPath('/'), labelKey: 'nav.overview', icon: 'dashboard' },
  { to: adminPath('/activity'), labelKey: 'nav.activity', icon: 'activity' },
  { to: adminPath('/tasks'), labelKey: 'nav.tasks', icon: 'tasks', permission: 'tasks.view' },
]

const staticResources: NavigationEntry[] = [
  { to: adminPath('/users'), labelKey: 'nav.users', icon: 'users', permission: 'users.view' },
  { to: adminPath('/roles'), labelKey: 'nav.roles', icon: 'roles', permission: 'roles.view' },
]

const staticManage: NavigationEntry[] = [
  { to: adminPath('/audit'), labelKey: 'nav.audit', icon: 'audit', permission: 'audit.view' },
  { to: adminPath('/introspection'), labelKey: 'nav.introspection', icon: 'database', permission: 'users.view' },
  { to: adminPath('/generator'), labelKey: 'nav.generator', icon: 'generator', permission: 'users.view' },
  { to: adminPath('/modules'), labelKey: 'nav.modules', icon: 'modules', permission: 'users.view' },
  { to: adminPath('/openapi-browser'), labelKey: 'nav.apiExplorer', icon: 'api', permission: 'users.view' },
  { to: adminPath('/permissions'), labelKey: 'nav.permissions', icon: 'permissions', permission: 'roles.view' },
  { to: adminPath('/settings'), labelKey: 'nav.settings', icon: 'settings' },
]

function manifestEntry(manifest: ResourceManifest): NavigationEntry {
  return {
    to: manifest.routes.list,
    labelKey: manifest.labelPlural,
    icon: manifest.name === 'roles' ? 'roles' : 'users',
    permission: manifest.permissions.view,
  }
}

export function buildNavigationRegistry(manifests: ResourceManifest[]): NavigationRegistry {
  const resources = manifests.length > 0 ? manifests.map(manifestEntry) : staticResources
  return {
    workspace: staticWorkspace,
    manage: [...resources, ...staticManage],
  }
}
