import type { ResourceManifest } from './types'

export function validateResourceForm(manifest: ResourceManifest, values: Record<string, string>): string | null {
  const editableFields = new Set([...manifest.forms.create.fields, ...manifest.forms.edit.fields])
  const field = manifest.fields.find((candidate) => editableFields.has(candidate.name) && !candidate.readonly && candidate.required && !String(values[candidate.name] ?? '').trim())
  return field ? `${field.name}Required` : null
}
