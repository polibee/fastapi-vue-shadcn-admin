import { describe, expect, it } from 'vitest'
import { assertResourceRouteBoundary } from './route-boundary'

describe('resource route boundary', () => {
  it('keeps UI routes and API bases in separate namespaces', () => {
    expect(() => assertResourceRouteBoundary({ routes: { list: '/admin/departments' }, api: { base: '/api/v1/departments' } })).not.toThrow()
    expect(() => assertResourceRouteBoundary({ routes: { list: '/departments' }, api: { base: '/api/v1/departments' } })).toThrow()
    expect(() => assertResourceRouteBoundary({ routes: { list: '/admin/departments' }, api: { base: '/departments' } })).toThrow()
  })
})
