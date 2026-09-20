<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, ShieldCheck, X } from '@lucide/vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { updateRoleDataScope, updateRolePermissions } from '@/core/api/resources'
import { loadResourceManifest, resourceAdapterRegistry, validateResourceForm } from '@/core/resources'
import { useResourceList } from '@/core/resources/useResourceList'
import type { ResourceManifest } from '@/core/resources/types'
import type { RoleFormValues } from '@/core/forms/resourceForms'
import { currentUser } from '@/core/permissions'
import type { RoleRead } from '@/core/api/generated/client'
import ResourcePageShell from './ResourcePageShell.vue'
import ResourceQueryBar from './ResourceQueryBar.vue'
import ResourceForm from './ResourceForm.vue'
import ResourceTable from './ResourceTable.vue'
import ResourceActionBar from './ResourceActionBar.vue'

const { t } = useI18n()
const formOpen = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const form = ref<RoleFormValues>({ name: '', description: '' })
const editingRoleId = ref<number | null>(null)
const permissionDraft = ref('')
const permissionError = ref(false)
const editingScopeId = ref<number | null>(null)
const scopeDraft = ref<'all' | 'self'>('all')
const scopeError = ref(false)
const roleManifest = ref<ResourceManifest | null>(null)
const selectedRoleIds = ref<number[]>([])
const search = ref('')
const pageSize = 10
const resourceAdapter = resourceAdapterRegistry.get<RoleRead, RoleFormValues>('roles')
const { items: roles, total, loading, error, page, sortBy, sortOrder, totalPages: listTotalPages, load: loadList, reset: resetList, changePage: changeListPage, setSort } = useResourceList<RoleRead>((query) => resourceAdapter.list({ offset: query.offset, limit: query.limit, sortBy: query.sortBy, sortOrder: query.sortOrder, search: search.value }), pageSize)
const totalPages = () => listTotalPages.value
const roleRows = computed(() => roles.value as unknown as Array<Record<string, unknown>>)
function asRole(row: Record<string, unknown>): RoleRead { return row as unknown as RoleRead }
function permissionsFor(row: Record<string, unknown>): string[] { return (row.permissions as string[] | undefined) ?? [] }
function handleRoleAction(role: RoleRead, action: string) {
  if (action === 'edit_permissions') startPermissionEdit(role)
  if (action === 'edit_scope') startScopeEdit(role)
  if (action === 'delete') void removeRole(role)
}

async function handleRoleBulkAction(action: string) {
  if (action !== 'delete_selected' || selectedRoleIds.value.length === 0) return
  if (!window.confirm(t('roles.bulkDeleteConfirm', { count: selectedRoleIds.value.length }))) return
  await resourceAdapter.bulkRemove(selectedRoleIds.value)
  selectedRoleIds.value = []
  await loadRoles()
}

async function loadRoles() {
  await loadList()
}

async function applyFilters() { await resetList() }
async function changePage(nextPage: number) { await changeListPage(nextPage) }

function resetForm() {
  form.value = { name: '', description: '' }
  formError.value = null
}

async function submitRole() {
  formError.value = roleManifest.value ? validateResourceForm(roleManifest.value, form.value) : 'nameRequired'
  if (formError.value) return
  submitting.value = true
  try {
    await resourceAdapter.create(form.value)
    formOpen.value = false
    resetForm()
    await loadRoles()
  } catch {
    formError.value = 'createFailed'
  } finally {
    submitting.value = false
  }
}

async function removeRole(role: RoleRead) {
  if (!window.confirm(t('roles.deleteConfirm', { name: role.name }))) return
  try {
    await resourceAdapter.remove(role.id)
    await loadRoles()
  } catch {
    error.value = true
  }
}

function startPermissionEdit(role: RoleRead) {
  editingRoleId.value = role.id
  permissionDraft.value = role.permissions.join(', ')
  permissionError.value = false
}

function cancelPermissionEdit() {
  editingRoleId.value = null
  permissionDraft.value = ''
  permissionError.value = false
}

function startScopeEdit(role: RoleRead) {
  editingScopeId.value = role.id
  scopeDraft.value = role.data_scope ?? 'all'
  scopeError.value = false
}

function cancelScopeEdit() {
  editingScopeId.value = null
  scopeDraft.value = 'all'
  scopeError.value = false
}

async function saveScope(role: RoleRead) {
  try {
    await updateRoleDataScope(role.id, scopeDraft.value)
    cancelScopeEdit()
    await loadRoles()
  } catch {
    scopeError.value = true
  }
}

async function savePermissions(role: RoleRead) {
  try {
    const codes = permissionDraft.value.split(',').map((code) => code.trim()).filter(Boolean)
    await updateRolePermissions(role.id, codes)
    cancelPermissionEdit()
    await loadRoles()
  } catch {
    permissionError.value = true
  }
}

onMounted(async () => {
  await Promise.all([loadRoles(), loadResourceManifest('roles').then((manifest) => { roleManifest.value = manifest }).catch(() => { roleManifest.value = null })])
})
</script>

<template>
  <ResourcePageShell :eyebrow="t('nav.manage')" :title="t('roles.title')" :description="t('roles.description')" :refresh-label="t('roles.refresh')" :create-label="t('roles.create')" :create-visible="!formOpen" :error="error" :error-title="t('roles.loadFailed')" :error-description="t('roles.loadFailed')" :loading="loading" @refresh="loadRoles" @create="formOpen = true">
    <Card v-if="formOpen"><CardHeader><CardTitle>{{ t('roles.create') }}</CardTitle><CardDescription>{{ t('roles.createDescription') }}</CardDescription></CardHeader><CardContent><ResourceForm v-if="roleManifest" v-model="form" :manifest="roleManifest" :submitting="submitting" :error-key="formError" translation-namespace="roles" :submit-label="submitting ? t('roles.creating') : t('roles.save')" :cancel-label="t('roles.cancel')" @submit="submitRole" @cancel="formOpen = false; resetForm()" /></CardContent></Card>
    <section class="grid gap-3"><div class="flex items-center justify-between"><div class="flex items-center gap-2"><ShieldCheck aria-hidden="true" /><h2 class="text-lg font-semibold">{{ t('roles.title') }}</h2></div><p class="text-sm text-muted-foreground">{{ t('roles.total', { count: total }) }}</p></div><ResourceQueryBar v-if="roleManifest" v-model:search="search" :sort-by="sortBy" :sort-order="sortOrder" :manifest="roleManifest" :search-placeholder="t('roles.searchPlaceholder')" label-namespace="roles" @update:sort-by="setSort($event, sortOrder)" @update:sort-order="setSort(sortBy, $event)" @submit="applyFilters" /><ResourceTable v-if="roleManifest" :manifest="roleManifest" :rows="roleRows" :permissions="currentUser?.permissions ?? []" selectable @selection-change="selectedRoleIds = $event" @bulk-action="handleRoleBulkAction($event)" :loading="loading" :empty-label="t('roles.empty')" label-namespace="roles"><template #actions="{ row }"><div class="grid justify-items-end gap-2"><ResourceActionBar :manifest="roleManifest" :permissions="currentUser?.permissions ?? []" @action="handleRoleAction(asRole(row), $event)" /><div class="flex flex-wrap justify-end gap-2"><Badge variant="secondary">{{ t(`roles.scope.${asRole(row).data_scope ?? 'all'}`) }}</Badge><Badge v-for="permission in permissionsFor(row)" :key="permission" variant="outline">{{ permission }}</Badge><span v-if="permissionsFor(row).length === 0" class="text-sm text-muted-foreground">{{ t('roles.noPermissions') }}</span></div><div v-if="editingRoleId === row.id" class="grid gap-2"><Input v-model="permissionDraft" :placeholder="t('roles.permissionsPlaceholder')" /><div class="flex gap-2"><Button size="sm" @click="savePermissions(asRole(row))"><Check data-icon="inline-start" aria-hidden="true" />{{ t('roles.savePermissions') }}</Button><Button size="sm" variant="outline" @click="cancelPermissionEdit"><X data-icon="inline-start" aria-hidden="true" />{{ t('roles.cancel') }}</Button></div><p v-if="permissionError" class="text-sm text-destructive">{{ t('roles.permissionUpdateFailed') }}</p></div><div v-if="editingScopeId === row.id" class="grid gap-2"><div class="flex gap-2"><Button size="sm" :variant="scopeDraft === 'all' ? 'default' : 'outline'" @click="scopeDraft = 'all'">{{ t('roles.scope.all') }}</Button><Button size="sm" :variant="scopeDraft === 'self' ? 'default' : 'outline'" @click="scopeDraft = 'self'">{{ t('roles.scope.self') }}</Button></div><div class="flex gap-2"><Button size="sm" @click="saveScope(asRole(row))"><Check data-icon="inline-start" aria-hidden="true" />{{ t('roles.saveScope') }}</Button><Button size="sm" variant="outline" @click="cancelScopeEdit"><X data-icon="inline-start" aria-hidden="true" />{{ t('roles.cancel') }}</Button></div><p v-if="scopeError" class="text-sm text-destructive">{{ t('roles.scopeUpdateFailed') }}</p></div></div></template></ResourceTable><div v-if="total > pageSize" class="flex items-center justify-between border-t pt-3 text-sm"><span class="text-muted-foreground">{{ t('roles.page', { page, pages: totalPages() }) }}</span><div class="flex gap-2"><Button variant="outline" size="sm" :disabled="loading || page <= 1" @click="changePage(page - 1)">{{ t('roles.previous') }}</Button><Button variant="outline" size="sm" :disabled="loading || page >= totalPages()" @click="changePage(page + 1)">{{ t('roles.next') }}</Button></div></div></section>
  </ResourcePageShell>
</template>
