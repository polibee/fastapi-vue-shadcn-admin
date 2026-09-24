import { describe, expect, it } from 'vitest'
import { generateSecurePassword } from './password'

describe('generateSecurePassword', () => {
  it('returns a copyable password with the requested length and character variety', () => {
    const password = generateSecurePassword(20)

    expect(password).toHaveLength(20)
    expect(password).toMatch(/[A-Z]/)
    expect(password).toMatch(/[a-z]/)
    expect(password).toMatch(/[0-9]/)
    expect(password).toMatch(/[^A-Za-z0-9]/)
  })
})
