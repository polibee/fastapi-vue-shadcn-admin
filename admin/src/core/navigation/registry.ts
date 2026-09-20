import type { ResourceManifest } from '@/core/resources/types'

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
  { to: '/', labelKey: 'nav.overview', icon: 'dashboard' },
  { to: '/activity', labelKey: 'nav.activity', icon: 'activity' },
  { to: '/tasks', labelKey: 'nav.tasks', icon: 'tasks', permission: 'tasks.view' },
]

const staticResources: NavigationEntry[] = [
  { to: '/users', labelKey: 'nav.users', icon: 'users', permission: 'users.view' },
  { to: '/roles', labelKey: 'nav.roles', icon: 'roles', permission: 'roles.view' },
]

const staticManage: NavigationEntry[] = [
  { to: '/audit', labelKey: 'nav.audit', icon: 'audit', permission: 'audit.view' },
  { to: '/introspection', labelKey: 'nav.introspection', icon: 'database', permission: 'users.view' },
  { to: '/generator', labelKey: 'nav.generator', icon: 'generator', permission: 'users.view' },
  { to: '/modules', labelKey: 'nav.modules', icon: 'modules', permission: 'users.view' },
  { to: '/openapi-browser', labelKey: 'nav.apiExplorer', icon: 'api', permission: 'users.view' },
  { to: '/permissions', labelKey: 'nav.permissions', icon: 'permissions', permission: 'roles.view' },
  { to: '/settings', labelKey: 'nav.settings', icon: 'settings' },
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
