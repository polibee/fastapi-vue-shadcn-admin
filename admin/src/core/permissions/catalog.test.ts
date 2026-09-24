import { describe, expect, it } from 'vitest'
import { groupPermissions } from './catalog'

describe('groupPermissions', () => {
  it('groups permission codes by their module prefix', () => {
    expect(groupPermissions([
      { id: 1, code: 'users.view', description: null, created_at: '' },
      { id: 2, code: 'users.delete', description: null, created_at: '' },
      { id: 3, code: 'roles.view', description: null, created_at: '' },
    ])).toEqual([
      { name: 'roles', items: [{ id: 3, code: 'roles.view', description: null, created_at: '' }] },
      { name: 'users', items: [
        { id: 2, code: 'users.delete', description: null, created_at: '' },
        { id: 1, code: 'users.view', description: null, created_at: '' },
      ] },
    ])
  })
})
