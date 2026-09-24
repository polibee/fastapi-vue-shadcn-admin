export function detailRoutePath(listPath: string): string {
  return `${listPath}/:id`
}

export function matchesResourceRoute(resourcePath: string, currentPath: string): boolean {
  return resourcePath === currentPath || currentPath.startsWith(`${resourcePath}/`)
}
