import { describe, expect, it } from 'vitest'
import { ADMIN_CATCH_ALL_PATH, ADMIN_ENTRY_PATH, LEGACY_ADMIN_PATHS, adminRoutePaths } from './route-paths'

describe('admin route table', () => {
  it('registers only the admin namespace for admin pages', () => {
    expect(adminRoutePaths).toEqual(expect.arrayContaining([
      '/admin/',
      '/admin/login',
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
    ]))
    expect(adminRoutePaths).not.toContain('/login')
    expect(adminRoutePaths).not.toContain('/users')
    expect(adminRoutePaths).not.toContain('/roles')
  })

  it('keeps legacy root admin paths outside the route table', () => {
    expect(ADMIN_ENTRY_PATH).toBe('/')
    expect(ADMIN_CATCH_ALL_PATH).toBe('/:pathMatch(.*)*')
    for (const path of LEGACY_ADMIN_PATHS) expect(adminRoutePaths).not.toContain(path)
  })

})
