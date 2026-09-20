import { describe, expect, it, vi } from 'vitest'

vi.mock('./generated/client', () => ({
  readDatabaseIntrospectionApiV1AdminIntrospectionGet: vi.fn(async () => ({ dialect: 'postgresql', schema: null, tables: [], views: [] })),
  readDatabaseCompatibilityApiV1AdminIntrospectionCompatibilityGet: vi.fn(async () => ({ items: [{ resource: 'roles', table: 'roles', status: 'ok', missingColumns: [], extraColumns: [] }] })),
}))

describe('introspection adapter', () => {
  it('returns the direct generated response', async () => {
    const { fetchDatabaseIntrospection } = await import('./introspection')
    await expect(fetchDatabaseIntrospection()).resolves.toEqual({ dialect: 'postgresql', schema: null, tables: [], views: [] })
  })

  it('returns compatibility items from the direct generated response', async () => {
    const { fetchResourceCompatibility } = await import('./introspection')
    await expect(fetchResourceCompatibility()).resolves.toEqual([{ resource: 'roles', table: 'roles', status: 'ok', missingColumns: [], extraColumns: [] }])
  })
})
