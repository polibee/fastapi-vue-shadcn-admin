export type UserFormValues = { username: string; email: string; password: string }
export type RoleFormValues = { name: string; description: string }

export function validateUserForm(values: UserFormValues): string | null {
  if (!values.username.trim()) return 'usernameRequired'
  if (!values.email.trim()) return 'emailRequired'
  if (!values.password.trim()) return 'passwordRequired'
  return null
}

export function validateRoleForm(values: RoleFormValues): string | null {
  if (!values.name.trim()) return 'nameRequired'
  return null
}
