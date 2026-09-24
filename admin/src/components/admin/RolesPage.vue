<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ShieldCheck } from '@lucide/vue'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useResourceList } from '@/core/resources/useResourceList'
import { loadResourceManifest, resourceAdapterRegistry, validateResourceForm } from '@/core/resources'
import { currentUser } from '@/core/permissions'
import type { ResourceManifest } from '@/core/resources/types'
import type { RoleFormValues } from '@/core/forms/resourceForms'
import type { RoleRead } from '@/core/api/generated/client'
import ResourcePageShell from './ResourcePageShell.vue'
import ResourceQueryBar from './ResourceQueryBar.vue'
import ResourceForm from './ResourceForm.vue'
import ResourceTable from './ResourceTable.vue'
import ResourceActionBar from './ResourceActionBar.vue'
import { adminPath } from '@/router/paths'

const { t } = useI18n()
const router = useRouter()
const formOpen = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const form = ref<RoleFormValues>({ name: '', description: '' })
const roleManifest = ref<ResourceManifest | null>(null)
const selectedRoleIds = ref<number[]>([])
const search = ref('')
const pageSize = 10
const resourceAdapter = resourceAdapterRegistry.get<RoleRead, RoleFormValues>('roles')
const { items: roles, total, loading, error, page, sortBy, sortOrder, totalPages: listTotalPages, load: loadList, reset: resetList, changePage: changeListPage, setSort } = useResourceList<RoleRead>((query) => resourceAdapter.list({ offset: query.offset, limit: query.limit, sortBy: query.sortBy, sortOrder: query.sortOrder, search: search.value }), pageSize)
const roleRows = computed(() => roles.value as unknown as Array<Record<string, unknown>>)
const totalPages = () => listTotalPages.value

function asRole(row: Record<string, unknown>): RoleRead { return row as unknown as RoleRead }
async function loadRoles() { await loadList() }
async function applyFilters() { await resetList() }
async function changePage(nextPage: number) { await changeListPage(nextPage) }
function resetForm() { form.value = { name: '', description: '' }; formError.value = null }

async function submitRole() {
  formError.value = roleManifest.value ? validateResourceForm(roleManifest.value, form.value) : 'nameRequired'
  if (formError.value) return
  submitting.value = true
  try { await resourceAdapter.create(form.value); formOpen.value = false; resetForm(); await loadRoles() } catch { formError.value = 'createFailed' } finally { submitting.value = false }
}

async function removeRole(role: RoleRead) {
  if (!window.confirm(t('roles.deleteConfirm', { name: role.name }))) return
  try { await resourceAdapter.remove(role.id); await loadRoles() } catch { error.value = true }
}

function openDetails(role: RoleRead) { void router.push(adminPath(`/roles/${role.id}`)) }
async function handleRoleAction(role: RoleRead, action: string) { if (action === 'edit') openDetails(role); else if (action === 'delete') await removeRole(role) }
async function handleRoleBulkAction(action: string) {
  if (action !== 'delete_selected' || selectedRoleIds.value.length === 0) return
  if (!window.confirm(t('roles.bulkDeleteConfirm', { count: selectedRoleIds.value.length }))) return
  await resourceAdapter.bulkRemove(selectedRoleIds.value); selectedRoleIds.value = []; await loadRoles()
}

onMounted(async () => { await Promise.all([loadRoles(), loadResourceManifest('roles').then((manifest) => { roleManifest.value = manifest }).catch(() => { roleManifest.value = null })]) })
</script>

<template>
  <ResourcePageShell :eyebrow="t('nav.manage')" :title="t('roles.title')" :description="t('roles.description')" :refresh-label="t('roles.refresh')" :create-label="t('roles.create')" :create-visible="!formOpen" :error="error" :error-title="t('roles.loadFailed')" :error-description="t('roles.loadFailed')" :loading="loading" @refresh="loadRoles" @create="formOpen = true">
    <Card v-if="formOpen"><CardHeader><CardTitle>{{ t('roles.create') }}</CardTitle><CardDescription>{{ t('roles.createDescription') }}</CardDescription></CardHeader><CardContent><ResourceForm v-if="roleManifest" v-model="form" :manifest="roleManifest" :submitting="submitting" :error-key="formError" translation-namespace="roles" :submit-label="submitting ? t('roles.creating') : t('roles.save')" :cancel-label="t('roles.cancel')" @submit="submitRole" @cancel="formOpen = false; resetForm()" /></CardContent></Card>
    <section class="grid gap-3"><div class="flex items-center justify-between"><div class="flex items-center gap-2"><ShieldCheck aria-hidden="true" /><h2 class="text-lg font-semibold">{{ t('roles.title') }}</h2></div><p class="text-sm text-muted-foreground">{{ t('roles.total', { count: total }) }}</p></div><ResourceQueryBar v-if="roleManifest" v-model:search="search" :sort-by="sortBy" :sort-order="sortOrder" :manifest="roleManifest" :search-placeholder="t('roles.searchPlaceholder')" label-namespace="roles" @update:sort-by="setSort($event, sortOrder)" @update:sort-order="setSort(sortBy, $event)" @submit="applyFilters" /><ResourceTable v-if="roleManifest" :manifest="roleManifest" :rows="roleRows" :permissions="currentUser?.permissions ?? []" selectable @selection-change="selectedRoleIds = $event" @bulk-action="handleRoleBulkAction($event)" :loading="loading" :empty-label="t('roles.empty')" label-namespace="roles"><template #actions="{ row }"><ResourceActionBar :manifest="roleManifest" :permissions="currentUser?.permissions ?? []" @action="handleRoleAction(asRole(row), $event)" /></template></ResourceTable><div v-if="total > pageSize" class="flex items-center justify-between border-t pt-3 text-sm"><span class="text-muted-foreground">{{ t('roles.page', { page, pages: totalPages() }) }}</span><div class="flex gap-2"><Button variant="outline" size="sm" :disabled="loading || page <= 1" @click="changePage(page - 1)">{{ t('roles.previous') }}</Button><Button variant="outline" size="sm" :disabled="loading || page >= totalPages()" @click="changePage(page + 1)">{{ t('roles.next') }}</Button></div></div></section>
  </ResourcePageShell>
</template>
