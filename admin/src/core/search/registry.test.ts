import { describe, expect, it } from 'vitest'
import { buildSearchRegistry } from './registry'

describe('global search registry', () => {
  it('builds unique searchable module entries from navigation', () => {
    const entries = buildSearchRegistry([
      { name: 'users', routes: { list: '/users' }, labelPlural: 'users.labelPlural', permissions: { view: 'users.view' } },
      { name: 'roles', routes: { list: '/roles' }, labelPlural: 'roles.labelPlural', permissions: { view: 'roles.view' } },
    ] as never)

    expect(entries.map((entry) => entry.to)).toEqual(['/','/activity','/tasks','/users','/roles','/audit','/introspection','/generator','/modules','/openapi-browser','/permissions','/settings'])
    expect(new Set(entries.map((entry) => entry.to)).size).toBe(entries.length)
    expect(entries.find((entry) => entry.to === '/users')?.permission).toBe('users.view')
  })
})
