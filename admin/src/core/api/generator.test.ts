import { describe, expect, it, vi } from 'vitest'

vi.mock('./generated/client', () => ({
  readCrudGenerationPlanApiV1AdminGeneratorPlansResourceGet: vi.fn(async () => ({ resource: 'users', module: 'server/app/modules/users', permissions: [], files: [] })),
}))

describe('generator adapter', () => {
  it('loads a read-only plan from the generated SDK', async () => {
    const { fetchCrudGenerationPlan } = await import('./generator')
    await expect(fetchCrudGenerationPlan('users')).resolves.toMatchObject({ resource: 'users' })
  })
})
