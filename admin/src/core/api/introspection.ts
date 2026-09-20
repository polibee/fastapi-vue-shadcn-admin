import { readDatabaseCompatibilityApiV1AdminIntrospectionCompatibilityGet, readDatabaseIntrospectionApiV1AdminIntrospectionGet } from './generated/client'
import { client } from './generated/client/client.gen'
import { getAccessToken } from './auth'

export type IntrospectionColumn = {
  name: string
  type: string
  nullable: boolean
  default: string | number | boolean | null
  primaryKey: boolean
  autoincrement: boolean | string | null
}

export type IntrospectionIndex = { name: string; unique: boolean; columns: string[] }
export type IntrospectionForeignKey = { name: string | null; columns: string[]; referredTable: string; referredSchema: string | null; referredColumns: string[] }
export type IntrospectionTable = { name: string; schema: string | null; columns: IntrospectionColumn[]; primaryKey: string[]; indexes: IntrospectionIndex[]; foreignKeys: IntrospectionForeignKey[] }
export type DatabaseIntrospection = { dialect: string; schema: string | null; tables: IntrospectionTable[]; views: string[] }
export type ResourceCompatibility = { resource: string; table: string; status: 'ok' | 'drift' | 'missing_table'; missingColumns: string[]; extraColumns: string[] }

export async function fetchDatabaseIntrospection(): Promise<DatabaseIntrospection> {
  client.setConfig({ baseUrl: '' })
  const result = await readDatabaseIntrospectionApiV1AdminIntrospectionGet({ auth: getAccessToken() ?? undefined, responseStyle: 'data', throwOnError: true })
  return result as unknown as DatabaseIntrospection
}

export async function fetchResourceCompatibility(): Promise<ResourceCompatibility[]> {
  client.setConfig({ baseUrl: '' })
  const result = await readDatabaseCompatibilityApiV1AdminIntrospectionCompatibilityGet({ auth: getAccessToken() ?? undefined, responseStyle: 'data', throwOnError: true })
  return (result as unknown as { items: ResourceCompatibility[] }).items
}
