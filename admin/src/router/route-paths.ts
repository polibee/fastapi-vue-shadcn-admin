export const adminRoutePaths = [
  '/admin/login',
  '/admin/',
  '/admin/activity',
  '/admin/tasks',
  '/admin/users',
  '/admin/roles',
  '/admin/departments',
  '/admin/audit',
  '/admin/settings',
  '/admin/introspection',
  '/admin/generator',
  '/admin/modules',
  '/admin/openapi-browser',
  '/admin/permissions',
] as const

export const LEGACY_ADMIN_PATHS = ['/login', '/users', '/roles', '/permissions', '/departments', '/tasks', '/audit', '/settings'] as const
export const ADMIN_ENTRY_PATH = '/'
export const ADMIN_CATCH_ALL_PATH = '/:pathMatch(.*)*'
