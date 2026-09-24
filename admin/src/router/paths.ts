export const ADMIN_ROUTE_PREFIX = '/admin'

export function adminPath(path = '/'): string {
  const child = path === '/' ? '' : path.replace(/^\/+/, '')
  return child ? `${ADMIN_ROUTE_PREFIX}/${child}` : `${ADMIN_ROUTE_PREFIX}/`
}

export function adminLoginPath(): string {
  return adminPath('/login')
}

export function isAdminPath(path: string): boolean {
  return path === ADMIN_ROUTE_PREFIX || path.startsWith(`${ADMIN_ROUTE_PREFIX}/`)
}

export function safeAdminRedirect(value: unknown): string {
  if (typeof value !== 'string' || value.startsWith('//') || !value.startsWith('/')) return adminPath('/')
  const pathname = value.split(/[?#]/, 1)[0]
  return isAdminPath(pathname) ? value : adminPath('/')
}
