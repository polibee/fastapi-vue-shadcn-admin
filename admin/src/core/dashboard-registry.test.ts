import { describe, expect, it } from 'vitest'
import { dashboardWidgetRegistry } from './dashboard-registry'

describe('dashboard widget registry', () => {
  it('defines stable stat and service widget contracts', () => {
    expect(dashboardWidgetRegistry.stats.map((widget) => widget.id)).toEqual(['activeUsers', 'queuedTasks', 'apiUptime', 'openIncidents'])
    expect(dashboardWidgetRegistry.services.map((widget) => widget.id)).toEqual(['api', 'worker', 'postgres', 'redis'])
    expect(dashboardWidgetRegistry.stats.find((widget) => widget.id === 'queuedTasks')?.valueSource).toBe('health.tasks.pending')
    expect(dashboardWidgetRegistry.services.find((widget) => widget.id === 'redis')?.healthSource).toBe('redis')
  })

  it('does not register duplicate widget IDs within a registry group', () => {
    const statIds = dashboardWidgetRegistry.stats.map((widget) => widget.id)
    const serviceIds = dashboardWidgetRegistry.services.map((widget) => widget.id)

    expect(new Set(statIds).size).toBe(statIds.length)
    expect(new Set(serviceIds).size).toBe(serviceIds.length)
  })
})
