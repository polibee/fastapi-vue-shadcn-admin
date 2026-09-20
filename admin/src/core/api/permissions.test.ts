import { describe, expect, it, vi } from 'vitest'

vi.mock('./generated/client', () => ({
  listPermissionsApiV1PermissionsGet: vi.fn(async () => ({ items: [{ id: 1, code: 'users.view' }], total: 1 })),
}))

describe('permissions adapter', () => {
  it('loads the generated permission catalog response', async () => {
    const { loadPermissions } = await import('./permissions')
    await expect(loadPermissions()).resolves.toMatchObject({ total: 1, items: [{ code: 'users.view' }] })
  })
})
