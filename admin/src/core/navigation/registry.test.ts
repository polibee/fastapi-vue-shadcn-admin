import { describe, expect, it } from 'vitest'
import { buildNavigationRegistry } from './registry'

describe('navigation registry', () => {
  it('merges manifest resources ahead of static resource fallbacks', () => {
    const navigation = buildNavigationRegistry([
      { name: 'users', routes: { list: '/admin/users' }, labelPlural: 'users.labelPlural', permissions: { view: 'users.view' } },
      { name: 'roles', routes: { list: '/admin/roles' }, labelPlural: 'roles.labelPlural', permissions: { view: 'roles.view' } },
    ] as never)

    expect(navigation.manage.filter((item) => item.to === '/admin/users')).toHaveLength(1)
    expect(navigation.manage.filter((item) => item.to === '/admin/roles')).toHaveLength(1)
    expect(navigation.manage.map((item) => item.to)).toEqual(['/admin/users', '/admin/roles', '/admin/audit', '/admin/introspection', '/admin/generator', '/admin/modules', '/admin/openapi-browser', '/admin/permissions', '/admin/settings'])
  })

  it('uses static resource entries when the manifest registry is unavailable', () => {
    const navigation = buildNavigationRegistry([])

    expect(navigation.manage.map((item) => item.to)).toEqual(['/admin/users', '/admin/roles', '/admin/audit', '/admin/introspection', '/admin/generator', '/admin/modules', '/admin/openapi-browser', '/admin/permissions', '/admin/settings'])
  })
})
