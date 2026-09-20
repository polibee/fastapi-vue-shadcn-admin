import { bulkDeleteRoles, bulkDeleteUsers, createRole, createUser, deleteRole, deleteUser, fetchRoles, fetchUsers } from '@/core/api/resources'
import type { RoleListResponse, RoleRead, UserListResponse, UserRead } from '@/core/api/generated/client'

export type ResourceListOptions = { offset?: number; limit?: number; search?: string; isActive?: boolean; sortBy?: string; sortOrder?: 'asc' | 'desc' }
export type ResourceAdapter<T, TCreate> = {
  list: (options?: ResourceListOptions) => Promise<{ items: T[]; total: number }>
  create: (input: TCreate) => Promise<T>
  remove: (id: number) => Promise<void>
  bulkRemove: (ids: number[]) => Promise<number[]>
}

class ResourceAdapterRegistry {
  private readonly adapters = new Map<string, ResourceAdapter<unknown, unknown>>()

  register<T, TCreate>(name: string, adapter: ResourceAdapter<T, TCreate>): void {
    this.adapters.set(name, adapter as ResourceAdapter<unknown, unknown>)
  }

  get<T, TCreate>(name: string): ResourceAdapter<T, TCreate> {
    const adapter = this.adapters.get(name)
    if (!adapter) throw new Error(`resource_adapter_not_registered:${name}`)
    return adapter as ResourceAdapter<T, TCreate>
  }
}

export const resourceAdapterRegistry = new ResourceAdapterRegistry()

resourceAdapterRegistry.register<UserRead, { username: string; email: string; password: string }>('users', {
  list: fetchUsers,
  create: createUser,
  remove: deleteUser,
  bulkRemove: bulkDeleteUsers,
})

resourceAdapterRegistry.register<RoleRead, { name: string; description: string }>('roles', {
  list: fetchRoles,
  create: createRole,
  remove: deleteRole,
  bulkRemove: bulkDeleteRoles,
})

export type RegisteredResourceResponse = UserListResponse | RoleListResponse
