import { describe, expect, it } from 'vitest'
import { canManageTask } from './tasks'

describe('task action permissions', () => {
  it('only exposes retry for retryable status when permission is present', () => {
    expect(canManageTask('failed', 'tasks.retry', [])).toBe(false)
    expect(canManageTask('pending', 'tasks.retry', ['tasks.retry'])).toBe(false)
    expect(canManageTask('failed', 'tasks.retry', ['tasks.retry'])).toBe(true)
  })

  it('only exposes cancellation for pending tasks when permission is present', () => {
    expect(canManageTask('succeeded', 'tasks.cancel', ['tasks.cancel'])).toBe(false)
    expect(canManageTask('pending', 'tasks.cancel', ['tasks.cancel'])).toBe(true)
  })
})
