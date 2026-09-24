import { describe, expect, it } from 'vitest'
import { detailRoutePath, matchesResourceRoute } from './resource-route-utils'

describe('resource route utilities', () => {
  it('uses the shared id parameter for generated detail routes', () => {
    expect(detailRoutePath('/admin/departments')).toBe('/admin/departments/:id')
  })

  it('matches list and detail paths without importing Vue components', () => {
    expect(matchesResourceRoute('/admin/departments', '/admin/departments')).toBe(true)
    expect(matchesResourceRoute('/admin/departments', '/admin/departments/1')).toBe(true)
    expect(matchesResourceRoute('/admin/departments', '/admin/department-settings')).toBe(false)
  })
})
