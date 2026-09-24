import type { RouteRecordRaw } from 'vue-router'
import type { Component } from 'vue'
import RolesPage from '@/components/admin/RolesPage.vue'
import RoleDetailPage from '@/components/admin/RoleDetailPage.vue'
import UsersPage from '@/components/admin/UsersPage.vue'
import GenericResourcePage from '@/components/admin/GenericResourcePage.vue'
import type { LocaleNamespace } from '@/locales'
import { adminPath } from './paths'

export type ResourceRouteRegistration = {
  name: string
  path: string
  permission: string
  namespaces: LocaleNamespace[]
  component: Component
  props?: Record<string, unknown>
}

export const resourceRouteRegistry: ResourceRouteRegistration[] = [
  { name: 'users', path: adminPath('/users'), permission: 'users.view', namespaces: ['common', 'shell', 'users'], component: UsersPage },
  { name: 'roles', path: adminPath('/roles'), permission: 'roles.view', namespaces: ['common', 'shell', 'roles'], component: RolesPage },
  { name: 'departments', path: adminPath('/departments'), permission: 'departments.view', namespaces: ['common', 'shell', 'users', 'roles', 'departments'], component: GenericResourcePage, props: { resourceName: 'departments', namespace: 'departments' } },
]

export const resourceRoutes: RouteRecordRaw[] = resourceRouteRegistry.map((resource) => ({
  path: resource.path,
  component: resource.component,
  props: resource.props,
  meta: { requiresAuth: true, permission: resource.permission, resource: resource.name },
}))

resourceRoutes.push({
  path: adminPath('/roles/:roleId'),
  component: RoleDetailPage,
  meta: { requiresAuth: true, permission: 'roles.view', resource: 'roles' },
})

export function namespacesForResourceRoute(path: string): LocaleNamespace[] | undefined {
  return resourceRouteRegistry.find((resource) => resource.path === path || (resource.name === 'roles' && path.startsWith(`${resource.path}/`)))?.namespaces
}

