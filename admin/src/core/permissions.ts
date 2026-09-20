import { ref } from 'vue'
import { fetchCurrentUser, type CurrentUser } from './api/auth'

const currentUser = ref<CurrentUser | null>(null)
const loading = ref(false)

export async function ensureCurrentUser(): Promise<CurrentUser> {
  if (currentUser.value) return currentUser.value
  loading.value = true
  try {
    currentUser.value = await fetchCurrentUser()
    return currentUser.value
  } finally {
    loading.value = false
  }
}

export function hasPermission(permission: string): boolean {
  return currentUser.value?.permissions.includes(permission) ?? false
}

export function clearCurrentUser(): void {
  currentUser.value = null
}

export { currentUser, loading }
