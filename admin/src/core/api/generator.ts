import { readCrudGenerationPlanApiV1AdminGeneratorPlansResourceGet } from './generated/client'
import { client } from './generated/client/client.gen'
import { getAccessToken } from './auth'

export type CrudGenerationPlan = { schemaVersion: string; generatorVersion: string; resource: string; module: string; permissions: string[]; files: Array<{ path: string; overwrite: 'never' | string }> }

export async function fetchCrudGenerationPlan(resource: string): Promise<CrudGenerationPlan> {
  client.setConfig({ baseUrl: '' })
  const result = await readCrudGenerationPlanApiV1AdminGeneratorPlansResourceGet({ auth: getAccessToken() ?? undefined, path: { resource }, responseStyle: 'data', throwOnError: true })
  return result as unknown as CrudGenerationPlan
}
