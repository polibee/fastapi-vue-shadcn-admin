import { describe, expect, it } from 'vitest'
import { validateRoleForm, validateUserForm } from './resourceForms'

describe('resource form validation', () => {
  it('requires username, email, and password for a user', () => {
    expect(validateUserForm({ username: '', email: '', password: '' })).toBe('usernameRequired')
    expect(validateUserForm({ username: 'admin', email: '', password: 'secret' })).toBe('emailRequired')
    expect(validateUserForm({ username: 'admin', email: 'admin@example.test', password: '' })).toBe('passwordRequired')
  })

  it('requires a role name', () => {
    expect(validateRoleForm({ name: ' ', description: '' })).toBe('nameRequired')
    expect(validateRoleForm({ name: 'operator', description: '' })).toBeNull()
  })
})
