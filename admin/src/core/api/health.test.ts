import { describe, expect, it, vi } from 'vitest';

const { healthApi, detailApi, setConfig } = vi.hoisted(() => ({
  healthApi: vi.fn(async () => ({ status: 'degraded', database: { status: 'up' }, redis: { status: 'down' } })),
  detailApi: vi.fn(async () => ({ status: 'ok', database: { status: 'up' }, redis: { status: 'up' }, tasks: { pending: 7 } })),
  setConfig: vi.fn(),
}))

vi.mock('./generated/client', () => ({
  healthApiV1HealthGet: healthApi,
  healthDetailApiV1HealthDetailGet: detailApi,
}))
vi.mock('./generated/client/client.gen', () => ({ client: { setConfig } }))
import { normalizeHealthPayload } from './health';

describe('normalizeHealthPayload', () => {
  it('normalizes the P2 health contract for the admin shell', () => {
    expect(normalizeHealthPayload({ status: 'ok', database: { status: 'up' }, redis: { status: 'down' }, tasks: { pending: 2 } })).toEqual({
      status: 'ok',
      database: 'ok',
      redis: 'unavailable',
      tasks: { total: 0, pending: 2, running: 0, failed: 0, dead: 0 },
    });
  });

  it('marks missing dependencies as unavailable instead of claiming healthy', () => {
    expect(normalizeHealthPayload({ status: 'ok' })).toEqual({
      status: 'ok',
      database: 'unavailable',
      redis: 'unavailable',
      tasks: { total: 0, pending: 0, running: 0, failed: 0, dead: 0 },
    });
  });
});

describe('health adapters', () => {
  it('uses the readiness-compatible health endpoint for shared page status', async () => {
    const { fetchHealth } = await import('./health')

    await expect(fetchHealth()).resolves.toMatchObject({ status: 'degraded', database: 'ok', redis: 'unavailable' })
    expect(healthApi).toHaveBeenCalledOnce()
    expect(detailApi).not.toHaveBeenCalled()
  })
})
