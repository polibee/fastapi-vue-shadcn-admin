import type { RouteRecordRaw } from 'vue-router'
import DashboardPage from '@/components/admin/DashboardPage.vue'
import ModulePlaceholder from '@/components/admin/ModulePlaceholder.vue'
import LoginPage from '@/components/admin/LoginPage.vue'
import AuditPage from '@/components/admin/AuditPage.vue'
import TasksPage from '@/components/admin/TasksPage.vue'
import SettingsPage from '@/components/admin/SettingsPage.vue'
import IntrospectionPage from '@/components/admin/IntrospectionPage.vue'
import GeneratorPage from '@/components/admin/GeneratorPage.vue'
import ModuleRegistryPage from '@/components/admin/ModuleRegistryPage.vue'
import OpenApiExplorerPage from '@/components/admin/OpenApiExplorerPage.vue'
import PermissionsPage from '@/components/admin/PermissionsPage.vue'
import { resourceRoutes } from './resource-routes'
import { adminRoutePaths } from './route-paths'

export const adminRouteRecords: RouteRecordRaw[] = [
  { path: '/admin/login', component: LoginPage, meta: { public: true } },
  { path: '/admin/', component: DashboardPage, meta: { requiresAuth: true } },
  { path: '/admin/activity', component: ModulePlaceholder, props: { titleKey: 'nav.activity' }, meta: { requiresAuth: true } },
  { path: '/admin/tasks', component: TasksPage, meta: { requiresAuth: true, permission: 'tasks.view' } },
  ...resourceRoutes,
  { path: '/admin/audit', component: AuditPage, meta: { requiresAuth: true, permission: 'audit.view' } },
  { path: '/admin/settings', component: SettingsPage, meta: { requiresAuth: true } },
  { path: '/admin/introspection', component: IntrospectionPage, meta: { requiresAuth: true, permission: 'users.view' } },
  { path: '/admin/generator', component: GeneratorPage, meta: { requiresAuth: true, permission: 'users.view' } },
  { path: '/admin/modules', component: ModuleRegistryPage, meta: { requiresAuth: true, permission: 'users.view' } },
  { path: '/admin/openapi-browser', component: OpenApiExplorerPage, meta: { requiresAuth: true, permission: 'users.view' } },
  { path: '/admin/permissions', component: PermissionsPage, meta: { requiresAuth: true, permission: 'roles.view' } },
]

export { adminRoutePaths }
