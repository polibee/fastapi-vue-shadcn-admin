import type { ResourceManifest } from './types'

export function validateResourceForm(manifest: ResourceManifest, values: Record<string, string>): string | null {
  const field = manifest.fields.find((candidate) => !candidate.readonly && candidate.required && !String(values[candidate.name] ?? '').trim())
  return field ? `${field.name}Required` : null
}
