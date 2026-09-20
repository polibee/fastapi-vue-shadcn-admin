export type OpenApiOperation = { path: string; method: string; summary: string; tags: string[] }
export type OpenApiDocument = { openapi: string; info: { title: string; version: string }; paths: Record<string, Record<string, { summary?: string; tags?: string[] }>> }

export async function fetchOpenApiDocument(): Promise<OpenApiDocument> {
  const response = await fetch('/openapi.json', { headers: { Accept: 'application/json' } })
  if (!response.ok) throw new Error(`OpenAPI request failed: ${response.status}`)
  return response.json() as Promise<OpenApiDocument>
}

export function listOpenApiOperations(document: OpenApiDocument): OpenApiOperation[] {
  return Object.entries(document.paths).flatMap(([path, operations]) => Object.entries(operations).filter(([method]) => method !== 'parameters').map(([method, operation]) => ({ path, method: method.toUpperCase(), summary: operation.summary ?? '', tags: operation.tags ?? [] }))).sort((left, right) => left.path.localeCompare(right.path) || left.method.localeCompare(right.method))
}
