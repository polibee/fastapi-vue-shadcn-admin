import type { PermissionRead } from '@/core/api/generated/client'

export type PermissionGroup = { name: string; items: PermissionRead[] }

export function groupPermissions(items: PermissionRead[]): PermissionGroup[] {
  const groups = new Map<string, PermissionRead[]>()
  for (const item of items) {
    const name = item.code.split('.', 1)[0] ?? 'other'
    groups.set(name, [...(groups.get(name) ?? []), item])
  }
  return [...groups.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([name, group]) => ({ name, items: group.sort((left, right) => left.code.localeCompare(right.code)) }))
}
