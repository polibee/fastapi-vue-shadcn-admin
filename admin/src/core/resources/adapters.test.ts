import { describe, expect, it } from 'vitest'
import { resourceAdapterRegistry } from './adapters'

describe('resource adapter registry', () => {
  it('registers the standard Users and Roles CRUD boundaries', () => {
    const users = resourceAdapterRegistry.get('users')
    const roles = resourceAdapterRegistry.get('roles')

    expect(typeof users.list).toBe('function')
    expect(typeof users.create).toBe('function')
    expect(typeof users.remove).toBe('function')
    expect(typeof users.bulkRemove).toBe('function')
    expect(typeof roles.list).toBe('function')
    expect(typeof roles.create).toBe('function')
    expect(typeof roles.remove).toBe('function')
    expect(typeof roles.bulkRemove).toBe('function')
  })

  it('fails fast when a resource has no adapter registration', () => {
    expect(() => resourceAdapterRegistry.get('missing')).toThrow('resource_adapter_not_registered:missing')
  })
})
