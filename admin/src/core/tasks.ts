const RETRYABLE_STATUSES = new Set(['failed', 'dead', 'cancelled'])

export function canManageTask(status: string, permission: 'tasks.cancel' | 'tasks.retry', permissions: string[]): boolean {
  const statusAllowed = permission === 'tasks.cancel'
    ? status === 'pending'
    : RETRYABLE_STATUSES.has(status)
  return statusAllowed && permissions.includes(permission)
}
