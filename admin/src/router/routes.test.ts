import { describe, expect, it } from 'vitest'
import { adminRoutePaths } from './route-paths'

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

})
