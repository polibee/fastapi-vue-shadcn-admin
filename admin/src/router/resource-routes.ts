import type { RouteRecordRaw } from 'vue-router'
import type { Component } from 'vue'
import RolesPage from '@/components/admin/RolesPage.vue'
import UsersPage from '@/components/admin/UsersPage.vue'
import GenericResourcePage from '@/components/admin/GenericResourcePage.vue'
import type { LocaleNamespace } from '@/locales'

export type ResourceRouteRegistration = {
  name: string
  path: string
  permission: string
  namespaces: LocaleNamespace[]
  component: Component
  props?: Record<string, unknown>
}

export const resourceRouteRegistry: ResourceRouteRegistration[] = [
  { name: 'users', path: '/users', permission: 'users.view', namespaces: ['common', 'shell', 'users'], component: UsersPage },
  { name: 'roles', path: '/roles', permission: 'roles.view', namespaces: ['common', 'shell', 'roles'], component: RolesPage },
  { name: 'departments', path: '/departments', permission: 'departments.view', namespaces: ['common', 'shell', 'users', 'roles', 'departments'], component: GenericResourcePage, props: { resourceName: 'departments', namespace: 'departments' } },
]

export const resourceRoutes: RouteRecordRaw[] = resourceRouteRegistry.map((resource) => ({
  path: resource.path,
  component: resource.component,
  props: resource.props,
  meta: { requiresAuth: true, permission: resource.permission, resource: resource.name },
}))

export function namespacesForResourceRoute(path: string): LocaleNamespace[] | undefined {
  return resourceRouteRegistry.find((resource) => resource.path === path)?.namespaces
}

