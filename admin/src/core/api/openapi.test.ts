import { describe, expect, it, vi } from 'vitest'
import { listOpenApiOperations } from './openapi'

describe('openapi adapter', () => {
  it('normalizes operations and ignores path parameters', () => {
    const operations = listOpenApiOperations({ openapi: '3.1.0', info: { title: 'Admin', version: '1' }, paths: { '/users': { get: { summary: 'List users', tags: ['Users'] }, parameters: {} }, '/health': { get: { tags: ['Health'] } } } })
    expect(operations).toEqual([{ path: '/health', method: 'GET', summary: '', tags: ['Health'] }, { path: '/users', method: 'GET', summary: 'List users', tags: ['Users'] }])
  })

  it('loads the live OpenAPI document', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, json: async () => ({ openapi: '3.1.0', info: { title: 'Admin', version: '1' }, paths: {} }) })))
    const { fetchOpenApiDocument } = await import('./openapi')
    await expect(fetchOpenApiDocument()).resolves.toMatchObject({ openapi: '3.1.0' })
    vi.unstubAllGlobals()
  })
})
