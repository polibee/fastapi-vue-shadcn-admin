<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, Users, X } from '@lucide/vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { updateUserRoles } from '@/core/api/resources'
import { loadResourceManifest, resourceAdapterRegistry, validateResourceForm } from '@/core/resources'
import { useResourceList } from '@/core/resources/useResourceList'
import type { ResourceManifest } from '@/core/resources/types'
import type { UserFormValues } from '@/core/forms/resourceForms'
import { currentUser } from '@/core/permissions'
import type { UserRead } from '@/core/api/generated/client'
import ResourcePageShell from './ResourcePageShell.vue'
import ResourceQueryBar from './ResourceQueryBar.vue'
import ResourceForm from './ResourceForm.vue'
import ResourceTable from './ResourceTable.vue'
import ResourceActionBar from './ResourceActionBar.vue'

const { t } = useI18n()
const formOpen = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const form = ref<UserFormValues>({ username: '', email: '', password: '' })
const editingUserId = ref<number | null>(null)
const roleDraft = ref('')
const roleError = ref(false)
const userManifest = ref<ResourceManifest | null>(null)
const selectedUserIds = ref<number[]>([])
const search = ref('')
const statusFilter = ref<'all' | 'active' | 'inactive'>('all')
const pageSize = 10
const resourceAdapter = resourceAdapterRegistry.get<UserRead, UserFormValues>('users')
const { items: users, total, loading, error, page, sortBy, sortOrder, totalPages: listTotalPages, load: loadList, reset: resetList, changePage: changeListPage, setSort } = useResourceList<UserRead>((query) => resourceAdapter.list({ offset: query.offset, limit: query.limit, sortBy: query.sortBy, sortOrder: query.sortOrder, search: search.value, isActive: statusFilter.value === 'all' ? undefined : statusFilter.value === 'active' }), pageSize)
const totalPages = () => listTotalPages.value
const userFilters = computed<Record<string, boolean | undefined>>({
  get: () => ({ is_active: statusFilter.value === 'all' ? undefined : statusFilter.value === 'active' }),
  set: (value) => { statusFilter.value = value.is_active === undefined ? 'all' : value.is_active ? 'active' : 'inactive' },
})
const userRows = computed(() => users.value as unknown as Array<Record<string, unknown>>)
function asUser(row: Record<string, unknown>): UserRead { return row as unknown as UserRead }
function rolesFor(row: Record<string, unknown>): string[] { return (row.roles as string[] | undefined) ?? [] }
async function handleUserAction(user: UserRead | Record<string, unknown>, action: string) {
  if (action === 'edit_roles') startRoleEdit(user as UserRead)
  if (action === 'delete') void removeUser(user as UserRead)
  if (action === 'delete_selected' && selectedUserIds.value.length > 0 && window.confirm(t('users.bulkDeleteConfirm', { count: selectedUserIds.value.length }))) {
    await resourceAdapter.bulkRemove(selectedUserIds.value)
    selectedUserIds.value = []
    await loadUsers()
  }
}

async function loadUsers() {
  await loadList()
}

async function applyFilters() {
  await resetList()
}

async function changePage(nextPage: number) {
  await changeListPage(nextPage)
}

function resetForm() {
  form.value = { username: '', email: '', password: '' }
  formError.value = null
}

async function submitUser() {
  formError.value = userManifest.value ? validateResourceForm(userManifest.value, form.value) : 'usernameRequired'
  if (formError.value) return
  submitting.value = true
  try {
    await resourceAdapter.create(form.value)
    formOpen.value = false
    resetForm()
    await loadUsers()
  } catch {
    formError.value = 'createFailed'
  } finally {
    submitting.value = false
  }
}

async function removeUser(user: UserRead) {
  if (!window.confirm(t('users.deleteConfirm', { username: user.username }))) return
  try {
    await resourceAdapter.remove(user.id)
    await loadUsers()
  } catch {
    error.value = true
  }
}

function startRoleEdit(user: UserRead) {
  editingUserId.value = user.id
  roleDraft.value = user.roles.join(', ')
  roleError.value = false
}

function cancelRoleEdit() {
  editingUserId.value = null
  roleDraft.value = ''
  roleError.value = false
}

async function saveRoles(user: UserRead) {
  try {
    const roles = roleDraft.value.split(',').map((role) => role.trim()).filter(Boolean)
    await updateUserRoles(user.id, roles)
    cancelRoleEdit()
    await loadUsers()
  } catch {
    roleError.value = true
  }
}

onMounted(async () => {
  await Promise.all([loadUsers(), loadResourceManifest('users').then((manifest) => { userManifest.value = manifest }).catch(() => { userManifest.value = null })])
})
</script>

<template>
  <ResourcePageShell :eyebrow="t('nav.manage')" :title="t('users.title')" :description="t('users.description')" :refresh-label="t('users.refresh')" :create-label="t('users.create')" :create-visible="!formOpen" :error="error" :error-title="t('users.loadFailed')" :error-description="t('users.loadFailed')" :loading="loading" @refresh="loadUsers" @create="formOpen = true">
    <Card v-if="formOpen"><CardHeader><CardTitle>{{ t('users.create') }}</CardTitle><CardDescription>{{ t('users.createDescription') }}</CardDescription></CardHeader><CardContent><ResourceForm v-if="userManifest" v-model="form" :manifest="userManifest" :submitting="submitting" :error-key="formError" :submit-label="submitting ? t('users.creating') : t('users.save')" :cancel-label="t('users.cancel')" @submit="submitUser" @cancel="formOpen = false; resetForm()" /></CardContent></Card>
    <section class="grid gap-3"><div class="flex items-center justify-between"><div class="flex items-center gap-2"><Users aria-hidden="true" /><h2 class="text-lg font-semibold">{{ t('users.title') }}</h2></div><p class="text-sm text-muted-foreground">{{ t('users.total', { count: total }) }}</p></div><ResourceQueryBar v-if="userManifest" v-model:search="search" v-model:filters="userFilters" :sort-by="sortBy" :sort-order="sortOrder" :manifest="userManifest" :search-placeholder="t('users.searchPlaceholder')" label-namespace="users" @update:sort-by="setSort($event, sortOrder)" @update:sort-order="setSort(sortBy, $event)" @submit="applyFilters" /><ResourceTable v-if="userManifest" :manifest="userManifest" :rows="userRows" :permissions="currentUser?.permissions ?? []" selectable @selection-change="selectedUserIds = $event" @bulk-action="handleUserAction({}, $event)" :loading="loading" :empty-label="t('users.empty')" label-namespace="users"><template #cell-is_active="{ value }"><Badge :variant="value ? 'secondary' : 'outline'">{{ value ? t('users.active') : t('users.inactive') }}</Badge></template><template #actions="{ row }"><div class="grid justify-items-end gap-2"><ResourceActionBar :manifest="userManifest" :permissions="currentUser?.permissions ?? []" @action="handleUserAction(asUser(row), $event)" /><div v-if="editingUserId === row.id" class="grid gap-2"><Input v-model="roleDraft" :placeholder="t('users.rolesPlaceholder')" /><div class="flex gap-2"><Button size="sm" @click="saveRoles(asUser(row))"><Check data-icon="inline-start" aria-hidden="true" />{{ t('users.saveRoles') }}</Button><Button size="sm" variant="outline" @click="cancelRoleEdit"><X data-icon="inline-start" aria-hidden="true" />{{ t('users.cancel') }}</Button></div><p v-if="roleError" class="text-sm text-destructive">{{ t('users.roleUpdateFailed') }}</p></div><div v-else class="flex flex-wrap justify-end gap-2"><Badge v-for="role in rolesFor(row)" :key="role" variant="outline">{{ role }}</Badge><span v-if="rolesFor(row).length === 0" class="text-sm text-muted-foreground">{{ t('users.noRoles') }}</span></div></div></template></ResourceTable><div v-if="total > pageSize" class="flex items-center justify-between border-t pt-3 text-sm"><span class="text-muted-foreground">{{ t('users.page', { page, pages: totalPages() }) }}</span><div class="flex gap-2"><Button variant="outline" size="sm" :disabled="loading || page <= 1" @click="changePage(page - 1)">{{ t('users.previous') }}</Button><Button variant="outline" size="sm" :disabled="loading || page >= totalPages()" @click="changePage(page + 1)">{{ t('users.next') }}</Button></div></div></section>
  </ResourcePageShell>
</template>
