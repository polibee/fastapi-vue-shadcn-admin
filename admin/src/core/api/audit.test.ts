import { beforeEach, describe, expect, it, vi } from 'vitest'

const { auditRequest, setConfig } = vi.hoisted(() => ({ auditRequest: vi.fn(), setConfig: vi.fn() }))

vi.mock('./generated/client', async (importOriginal) => ({
  ...(await importOriginal<typeof import('./generated/client')>()),
  listAuditLogsApiV1AuditLogsGet: auditRequest,
}))
vi.mock('./generated/client/client.gen', () => ({ client: { setConfig } }))

import { fetchAuditLogs } from './resources'

describe('audit API adapter', () => {
  beforeEach(() => {
    auditRequest.mockReset()
    setConfig.mockReset()
    auditRequest.mockResolvedValue({ items: [], total: 0, offset: 10, limit: 2 })
  })

  it('passes search and pagination to the generated SDK', async () => {
    await fetchAuditLogs({ search: 'role', offset: 10, limit: 2 })

    expect(auditRequest).toHaveBeenCalledWith(expect.objectContaining({
      query: { offset: 10, limit: 2, search: 'role' },
      responseStyle: 'data',
    }))
  })
})
