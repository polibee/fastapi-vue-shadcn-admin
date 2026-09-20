export type DashboardStatWidget = {
  id: 'activeUsers' | 'queuedTasks' | 'apiUptime' | 'openIncidents'
  labelKey: string
  icon: 'users' | 'tasks' | 'api' | 'activity'
  valueSource: 'unavailable' | 'health.tasks.pending'
  changeKey: 'notAvailable' | 'needsReview'
  detailKey: 'last30Days' | 'yesterday' | 'mediumLow'
}

export type DashboardServiceWidget = {
  id: 'api' | 'worker' | 'postgres' | 'redis'
  labelKey: string
  icon: 'api' | 'worker' | 'database' | 'redis'
  healthSource: 'api' | 'worker' | 'database' | 'redis'
}

export const dashboardWidgetRegistry = {
  stats: [
    { id: 'activeUsers', labelKey: 'dashboard.stats.activeUsers', icon: 'users', valueSource: 'unavailable', changeKey: 'notAvailable', detailKey: 'last30Days' },
    { id: 'queuedTasks', labelKey: 'dashboard.stats.queuedTasks', icon: 'tasks', valueSource: 'health.tasks.pending', changeKey: 'notAvailable', detailKey: 'yesterday' },
    { id: 'apiUptime', labelKey: 'dashboard.stats.apiUptime', icon: 'api', valueSource: 'unavailable', changeKey: 'notAvailable', detailKey: 'last30Days' },
    { id: 'openIncidents', labelKey: 'dashboard.stats.openIncidents', icon: 'activity', valueSource: 'unavailable', changeKey: 'needsReview', detailKey: 'mediumLow' },
  ] satisfies DashboardStatWidget[],
  services: [
    { id: 'api', labelKey: 'dashboard.health.api', icon: 'api', healthSource: 'api' },
    { id: 'worker', labelKey: 'dashboard.health.worker', icon: 'worker', healthSource: 'worker' },
    { id: 'postgres', labelKey: 'dashboard.health.postgres', icon: 'database', healthSource: 'database' },
    { id: 'redis', labelKey: 'dashboard.health.redis', icon: 'redis', healthSource: 'redis' },
  ] satisfies DashboardServiceWidget[],
} as const
