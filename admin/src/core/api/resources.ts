import {
  bulkDeleteDepartmentsApiV1DepartmentsBulkDeletePost,
  bulkDeleteRolesApiV1RolesBulkDeletePost,
  bulkDeleteUsersApiV1UsersBulkDeletePost,
  cancelTaskApiV1TasksTaskIdCancelPost,
  createDepartmentApiV1DepartmentsPost,
  createRoleApiV1RolesPost,
  createTaskApiV1TasksPost,
  createUserApiV1UsersPost,
  deleteDepartmentApiV1DepartmentsDepartmentIdDelete,
  deleteRoleApiV1RolesRoleIdDelete,
  deleteUserApiV1UsersUserIdDelete,
  listAuditLogsApiV1AuditLogsGet,
  listDepartmentsApiV1DepartmentsGet,
  listRolesApiV1RolesGet,
  listTaskEventsApiV1TasksTaskIdEventsGet,
  listTasksApiV1TasksGet,
  listUsersApiV1UsersGet,
  retryTaskApiV1TasksTaskIdRetryPost,
  updateDepartmentApiV1DepartmentsDepartmentIdPut,
  updateRolePermissionsApiV1RolesRoleIdPermissionsPut,
  updateRoleDataScopeApiV1RolesRoleIdDataScopePut,
  updateUserRolesApiV1UsersUserIdRolesPut,
} from './generated/client'
import { client } from './generated/client/client.gen'
import { getAccessToken } from './auth'
import type { RoleListResponse, RoleRead, UserListResponse, UserRead } from './generated/client'

export type AuditLogItem = { id: number; actor_user_id: number | null; action: string; resource: string; resource_id: number | null; request_id: string; created_at: string }
export type AuditLogResponse = { items: AuditLogItem[]; total: number; offset: number; limit: number }
export type TaskItem = { id: number; task_id: string; task_name: string; status: string; progress: number; message: string | null; attempts: number; max_attempts: number; started_at: string | null; error_message: string | null; payload: Record<string, unknown>; requested_by: number | null; request_id: string; broker_job_id: string | null; published_at: string | null; created_at: string; updated_at: string }
export type TaskEvent = { id: number; event_type: string; message: string | null; status: string | null; progress: number | null; created_at: string }
export type TaskResponse = { items: TaskItem[]; total: number; offset: number; limit: number }

export async function fetchUsers(options: { offset?: number; limit?: number; search?: string; isActive?: boolean; sortBy?: string; sortOrder?: 'asc' | 'desc' } = {}): Promise<UserListResponse> {
  client.setConfig({ baseUrl: '' })
  const result = await listUsersApiV1UsersGet({ auth: getAccessToken() ?? undefined, query: { offset: options.offset ?? 0, limit: options.limit ?? 20, search: options.search || undefined, is_active: options.isActive, sort_by: options.sortBy as 'id' | 'username' | 'email' | undefined, sort_order: options.sortOrder }, responseStyle: 'data', throwOnError: true })
  return result as unknown as UserListResponse
}

export async function fetchRoles(options: { offset?: number; limit?: number; search?: string; sortBy?: string; sortOrder?: 'asc' | 'desc' } = {}): Promise<RoleListResponse> {
  client.setConfig({ baseUrl: '' })
  const result = await listRolesApiV1RolesGet({ auth: getAccessToken() ?? undefined, query: { offset: options.offset ?? 0, limit: options.limit ?? 20, search: options.search || undefined, sort_by: options.sortBy as 'id' | 'name' | undefined, sort_order: options.sortOrder }, responseStyle: 'data', throwOnError: true })
  return result as unknown as RoleListResponse
}

export async function createUser(input: { username: string; email: string; password: string }): Promise<UserRead> {
  client.setConfig({ baseUrl: '' })
  const result = await createUserApiV1UsersPost({
    auth: getAccessToken() ?? undefined,
    body: { username: input.username, email: input.email, password_hash: input.password },
    responseStyle: 'data',
    throwOnError: true,
  })
  return result as unknown as UserRead
}

export async function createRole(input: { name: string; description: string }): Promise<RoleRead> {
  client.setConfig({ baseUrl: '' })
  const result = await createRoleApiV1RolesPost({
    auth: getAccessToken() ?? undefined,
    body: { name: input.name, description: input.description || null },
    responseStyle: 'data',
    throwOnError: true,
  })
  return result as unknown as RoleRead
}

export function deleteUser(userId: number): Promise<void> {
  client.setConfig({ baseUrl: '' })
  return deleteUserApiV1UsersUserIdDelete({ auth: getAccessToken() ?? undefined, path: { user_id: userId }, responseStyle: 'data', throwOnError: true }).then(() => undefined)
}

export async function bulkDeleteUsers(ids: number[]): Promise<number[]> {
  client.setConfig({ baseUrl: '' })
  const result = await bulkDeleteUsersApiV1UsersBulkDeletePost({ auth: getAccessToken() ?? undefined, body: { ids }, responseStyle: 'data', throwOnError: true })
  return (result as unknown as { deleted_ids: number[] }).deleted_ids
}

export function deleteRole(roleId: number): Promise<void> {
  client.setConfig({ baseUrl: '' })
  return deleteRoleApiV1RolesRoleIdDelete({ auth: getAccessToken() ?? undefined, path: { role_id: roleId }, responseStyle: 'data', throwOnError: true }).then(() => undefined)
}

export async function bulkDeleteRoles(ids: number[]): Promise<number[]> {
  client.setConfig({ baseUrl: '' })
  const result = await bulkDeleteRolesApiV1RolesBulkDeletePost({ auth: getAccessToken() ?? undefined, body: { ids }, responseStyle: 'data', throwOnError: true })
  return (result as unknown as { deleted_ids: number[] }).deleted_ids
}

export async function updateRolePermissions(roleId: number, codes: string[]): Promise<RoleRead> {
  client.setConfig({ baseUrl: '' })
  const result = await updateRolePermissionsApiV1RolesRoleIdPermissionsPut({ auth: getAccessToken() ?? undefined, path: { role_id: roleId }, body: { codes }, responseStyle: 'data', throwOnError: true })
  return result as unknown as RoleRead
}

export async function updateRoleDataScope(roleId: number, dataScope: 'all' | 'self'): Promise<RoleRead> {
  client.setConfig({ baseUrl: '' })
  const result = await updateRoleDataScopeApiV1RolesRoleIdDataScopePut({ auth: getAccessToken() ?? undefined, path: { role_id: roleId }, body: { data_scope: dataScope }, responseStyle: 'data', throwOnError: true })
  return result as unknown as RoleRead
}

export async function updateUserRoles(userId: number, roles: string[]): Promise<UserRead> {
  client.setConfig({ baseUrl: '' })
  const result = await updateUserRolesApiV1UsersUserIdRolesPut({ auth: getAccessToken() ?? undefined, path: { user_id: userId }, body: { roles }, responseStyle: 'data', throwOnError: true })
  return result as unknown as UserRead
}

export async function fetchAuditLogs(options: { offset?: number; limit?: number; search?: string } = {}): Promise<AuditLogResponse> {
  client.setConfig({ baseUrl: '' })
  const result = await listAuditLogsApiV1AuditLogsGet({ auth: getAccessToken() ?? undefined, query: { offset: options.offset ?? 0, limit: options.limit ?? 50, search: options.search || undefined }, responseStyle: 'data', throwOnError: true })
  return result as unknown as AuditLogResponse
}

export async function fetchTasks(): Promise<TaskResponse> {
  client.setConfig({ baseUrl: '' })
  const result = await listTasksApiV1TasksGet({ auth: getAccessToken() ?? undefined, query: { offset: 0, limit: 50 }, responseStyle: 'data', throwOnError: true })
  return result as unknown as TaskResponse
}

export async function fetchTaskEvents(taskId: string): Promise<TaskEvent[]> {
  client.setConfig({ baseUrl: '' })
  const response = await listTaskEventsApiV1TasksTaskIdEventsGet({ auth: getAccessToken() ?? undefined, path: { task_id: taskId }, responseStyle: 'data', throwOnError: true })
  const payload = response as unknown as { items: TaskEvent[] }
  return payload.items
}

export async function createTask(taskName: string, payload: Record<string, unknown>): Promise<TaskItem> {
  client.setConfig({ baseUrl: '' })
  const result = await createTaskApiV1TasksPost({ auth: getAccessToken() ?? undefined, body: { task_name: taskName, payload }, responseStyle: 'data', throwOnError: true })
  return result as unknown as TaskItem
}

export async function cancelTask(taskId: string): Promise<void> {
  client.setConfig({ baseUrl: '' })
  await cancelTaskApiV1TasksTaskIdCancelPost({ auth: getAccessToken() ?? undefined, path: { task_id: taskId }, responseStyle: 'data', throwOnError: true })
}

export async function retryTask(taskId: string): Promise<TaskItem> {
  client.setConfig({ baseUrl: '' })
  const result = await retryTaskApiV1TasksTaskIdRetryPost({ auth: getAccessToken() ?? undefined, path: { task_id: taskId }, responseStyle: 'data', throwOnError: true })
  return result as unknown as TaskItem
}



export type DepartmentRead = { id: number; name: string; code: string; description: string | null; is_active: boolean; created_at: string }
export type DepartmentInput = { name: string; code: string; description?: string | null; is_active?: boolean }
export type DepartmentListResponse = { items: DepartmentRead[]; total: number; offset: number; limit: number }
export async function fetchDepartments(options: { offset?: number; limit?: number; search?: string; isActive?: boolean; sortBy?: string; sortOrder?: 'asc' | 'desc' } = {}): Promise<DepartmentListResponse> { client.setConfig({ baseUrl: '' }); const result = await listDepartmentsApiV1DepartmentsGet({ auth: getAccessToken() ?? undefined, query: { offset: options.offset ?? 0, limit: options.limit ?? 20, search: options.search || undefined, is_active: options.isActive, sort_by: options.sortBy as 'id' | 'name' | 'code' | undefined, sort_order: options.sortOrder }, responseStyle: 'data', throwOnError: true }); return result as unknown as DepartmentListResponse }
export async function createDepartment(input: DepartmentInput): Promise<DepartmentRead> { client.setConfig({ baseUrl: '' }); const result = await createDepartmentApiV1DepartmentsPost({ auth: getAccessToken() ?? undefined, body: { name: input.name, code: input.code, description: input.description || null, is_active: input.is_active ?? true }, responseStyle: 'data', throwOnError: true }); return result as unknown as DepartmentRead }
export async function updateDepartment(id: number, input: DepartmentInput): Promise<DepartmentRead> { client.setConfig({ baseUrl: '' }); const result = await updateDepartmentApiV1DepartmentsDepartmentIdPut({ auth: getAccessToken() ?? undefined, path: { department_id: id }, body: { name: input.name, code: input.code, description: input.description || null, is_active: input.is_active ?? true }, responseStyle: 'data', throwOnError: true }); return result as unknown as DepartmentRead }
export function deleteDepartment(id: number): Promise<void> { client.setConfig({ baseUrl: '' }); return deleteDepartmentApiV1DepartmentsDepartmentIdDelete({ auth: getAccessToken() ?? undefined, path: { department_id: id }, responseStyle: 'data', throwOnError: true }).then(() => undefined) }
export async function bulkDeleteDepartments(ids: number[]): Promise<number[]> { client.setConfig({ baseUrl: '' }); const result = await bulkDeleteDepartmentsApiV1DepartmentsBulkDeletePost({ auth: getAccessToken() ?? undefined, body: { ids }, responseStyle: 'data', throwOnError: true }); return (result as unknown as { deleted_ids: number[] }).deleted_ids }
