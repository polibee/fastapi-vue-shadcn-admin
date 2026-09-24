import { describe, expect, it } from 'vitest'
import { ADMIN_ROUTE_PREFIX, adminLoginPath, adminPath, isAdminPath, safeAdminRedirect } from './paths'

describe('admin route paths', () => {
  it('prefixes child paths and normalizes slashes', () => {
    expect(ADMIN_ROUTE_PREFIX).toBe('/admin')
    expect(adminPath('/users')).toBe('/admin/users')
    expect(adminPath('users')).toBe('/admin/users')
    expect(adminPath('/')).toBe('/admin/')
    expect(adminLoginPath()).toBe('/admin/login')
  })

  it('recognizes only the admin frontend namespace', () => {
    expect(isAdminPath('/admin')).toBe(true)
    expect(isAdminPath('/admin/users')).toBe(true)
    expect(isAdminPath('/users')).toBe(false)
    expect(isAdminPath('/api/v1/users')).toBe(false)
  })

  it('keeps redirect targets inside the admin namespace', () => {
    expect(safeAdminRedirect('/admin/users')).toBe('/admin/users')
    expect(safeAdminRedirect('https://evil.example')).toBe('/admin/')
    expect(safeAdminRedirect('//evil.example')).toBe('/admin/')
    expect(safeAdminRedirect('/users')).toBe('/admin/')
  })
})
