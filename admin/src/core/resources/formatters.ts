import type { ResourceField } from './types'

export function formatResourceValue(field: ResourceField, value: unknown, emptyValue = '—'): string {
  if (value === null || value === undefined || value === '') return emptyValue
  if (field.type === 'boolean') return value ? 'true' : 'false'
  if (field.type === 'datetime' && typeof value === 'string') return new Date(value).toLocaleString()
  if (Array.isArray(value)) return value.join(', ')
  return String(value)
}
