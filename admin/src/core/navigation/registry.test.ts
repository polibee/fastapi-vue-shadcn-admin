import { describe, expect, it } from 'vitest'
import { buildNavigationRegistry } from './registry'

describe('navigation registry', () => {
  it('merges manifest resources ahead of static resource fallbacks', () => {
    const navigation = buildNavigationRegistry([
      { name: 'users', routes: { list: '/users' }, labelPlural: 'users.labelPlural', permissions: { view: 'users.view' } },
      { name: 'roles', routes: { list: '/roles' }, labelPlural: 'roles.labelPlural', permissions: { view: 'roles.view' } },
    ] as never)

    expect(navigation.manage.filter((item) => item.to === '/users')).toHaveLength(1)
    expect(navigation.manage.filter((item) => item.to === '/roles')).toHaveLength(1)
    expect(navigation.manage.map((item) => item.to)).toEqual(['/users', '/roles', '/audit', '/introspection', '/generator', '/modules', '/openapi-browser', '/permissions', '/settings'])
  })

  it('uses static resource entries when the manifest registry is unavailable', () => {
    const navigation = buildNavigationRegistry([])

    expect(navigation.manage.map((item) => item.to)).toEqual(['/users', '/roles', '/audit', '/introspection', '/generator', '/modules', '/openapi-browser', '/permissions', '/settings'])
  })
})
