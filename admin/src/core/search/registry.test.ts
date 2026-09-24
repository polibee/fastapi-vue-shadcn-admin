import { describe, expect, it } from 'vitest'
import { buildSearchRegistry } from './registry'

describe('global search registry', () => {
  it('builds unique searchable module entries from navigation', () => {
    const entries = buildSearchRegistry([
      { name: 'users', routes: { list: '/admin/users' }, labelPlural: 'users.labelPlural', permissions: { view: 'users.view' } },
      { name: 'roles', routes: { list: '/admin/roles' }, labelPlural: 'roles.labelPlural', permissions: { view: 'roles.view' } },
    ] as never)

    expect(entries.map((entry) => entry.to)).toEqual(['/admin/','/admin/activity','/admin/tasks','/admin/users','/admin/roles','/admin/audit','/admin/introspection','/admin/generator','/admin/modules','/admin/openapi-browser','/admin/permissions','/admin/settings'])
    expect(new Set(entries.map((entry) => entry.to)).size).toBe(entries.length)
    expect(entries.find((entry) => entry.to === '/admin/users')?.permission).toBe('users.view')
  })
})
