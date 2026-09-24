export type ResourceFieldType = 'text' | 'email' | 'password' | 'boolean' | 'datetime'

export interface ResourceField {
  name: string
  type: ResourceFieldType
  label: string
  required: boolean
  nullable: boolean
  readonly: boolean
  searchable: boolean
  sortable: boolean
  filterable: boolean
}

export interface ResourceManifest {
  schemaVersion: '1.0'
  name: string
  label: string
  labelPlural: string
  routes: { list: string; detail?: string }
  api: { base: string }
  permissions: Record<string, string>
  features: Record<string, boolean>
  query: ResourceQuery
  fields: ResourceField[]
  table: { columns: string[] }
  forms: { create: { fields: string[] }; edit: { fields: string[] } }
  actions: ResourceAction[]
  bulkActions: ResourceBulkAction[]
  relations: unknown[]
}

export interface ResourceQuery {
  searchFields: string[]
  filterFields: string[]
  sortFields: string[]
  defaultSort: { field: string; direction: 'asc' | 'desc' }
}

export interface ResourceAction {
  name: string
  label: string
  permission: string
  variant: string
  icon: 'edit' | 'delete' | 'more' | string
}

export interface ResourceBulkAction extends ResourceAction {}
