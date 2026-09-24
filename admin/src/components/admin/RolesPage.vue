<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, Search, ShieldCheck } from '@lucide/vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Sheet, SheetContent, SheetDescription, SheetFooter, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { updateRoleDataScope, updateRolePermissions } from '@/core/api/resources'
import { loadPermissions } from '@/core/api/permissions'
import { loadResourceManifest, resourceAdapterRegistry, validateResourceForm } from '@/core/resources'
import { groupPermissions, type PermissionGroup } from '@/core/permissions/catalog'
import { useResourceList } from '@/core/resources/useResourceList'
import type { ResourceManifest } from '@/core/resources/types'
import type { RoleFormValues } from '@/core/forms/resourceForms'
import { currentUser } from '@/core/permissions'
import type { PermissionRead, RoleRead } from '@/core/api/generated/client'
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
const roleManifest = ref<ResourceManifest | null>(null)
const selectedRoleIds = ref<number[]>([])
const search = ref('')
const pageSize = 10
const resourceAdapter = resourceAdapterRegistry.get<RoleRead, RoleFormValues>('roles')
const { items: roles, total, loading, error, page, sortBy, sortOrder, totalPages: listTotalPages, load: loadList, reset: resetList, changePage: changeListPage, setSort } = useResourceList<RoleRead>((query) => resourceAdapter.list({ offset: query.offset, limit: query.limit, sortBy: query.sortBy, sortOrder: query.sortOrder, search: search.value }), pageSize)
const roleRows = computed(() => roles.value as unknown as Array<Record<string, unknown>>)
const totalPages = () => listTotalPages.value

const detailsOpen = ref(false)
const detailsSaving = ref(false)
const detailsError = ref(false)
const selectedRole = ref<RoleRead | null>(null)
const detailsForm = ref<RoleFormValues>({ name: '', description: '' })
const detailsScope = ref<'all' | 'self'>('all')
const permissions = ref<PermissionRead[]>([])
const selectedPermissionCodes = ref<string[]>([])
const permissionSearch = ref('')
const permissionGroups = computed<PermissionGroup[]>(() => groupPermissions(permissions.value).map((group) => ({ ...group, items: group.items.filter((item) => item.code.toLowerCase().includes(permissionSearch.value.toLowerCase())) })).filter((group) => group.items.length))
const allVisibleCodes = computed(() => permissionGroups.value.flatMap((group) => group.items.map((item) => item.code)))
const isAdministrator = computed(() => selectedRole.value?.name === 'administrator')

function asRole(row: Record<string, unknown>): RoleRead { return row as unknown as RoleRead }
function permissionsFor(row: Record<string, unknown>): string[] { return (row.permissions as string[] | undefined) ?? [] }
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

async function openDetails(role: RoleRead): Promise<void> {
  selectedRole.value = role
  detailsForm.value = { name: role.name, description: role.description ?? '' }
  detailsScope.value = role.data_scope ?? 'all'
  permissionSearch.value = ''
  detailsError.value = false
  detailsOpen.value = true
  try {
    const result = await loadPermissions()
    permissions.value = result.items
    selectedPermissionCodes.value = role.name === 'administrator' ? result.items.map((item) => item.code) : [...role.permissions]
  } catch { detailsError.value = true }
}
function closeDetails() { detailsOpen.value = false; selectedRole.value = null }
function isSelected(code: string) { return selectedPermissionCodes.value.includes(code) }
function togglePermission(code: string) { if (!isAdministrator.value) selectedPermissionCodes.value = isSelected(code) ? selectedPermissionCodes.value.filter((item) => item !== code) : [...selectedPermissionCodes.value, code] }
function toggleGroup(group: PermissionGroup) { if (isAdministrator.value) return; const codes = group.items.map((item) => item.code); const allSelected = codes.every((code) => isSelected(code)); selectedPermissionCodes.value = allSelected ? selectedPermissionCodes.value.filter((code) => !codes.includes(code)) : [...new Set([...selectedPermissionCodes.value, ...codes])] }
function selectAllVisible() { if (!isAdministrator.value) selectedPermissionCodes.value = [...new Set([...selectedPermissionCodes.value, ...allVisibleCodes.value])] }
function clearVisible() { if (!isAdministrator.value) selectedPermissionCodes.value = selectedPermissionCodes.value.filter((code) => !allVisibleCodes.value.includes(code)) }

async function saveDetails() {
  if (!selectedRole.value || !roleManifest.value) return
  detailsSaving.value = true; detailsError.value = false
  try {
    const validation = validateResourceForm(roleManifest.value, detailsForm.value)
    if (validation) throw new Error(validation)
    await resourceAdapter.update?.(selectedRole.value.id, detailsForm.value)
    await updateRoleDataScope(selectedRole.value.id, detailsScope.value)
    await updateRolePermissions(selectedRole.value.id, selectedPermissionCodes.value)
    closeDetails(); await loadRoles()
  } catch { detailsError.value = true } finally { detailsSaving.value = false }
}

async function handleRoleAction(role: RoleRead, action: string) {
  if (action === 'edit' || action === 'edit_permissions' || action === 'edit_scope') await openDetails(role)
  if (action === 'delete') await removeRole(role)
}
async function handleRoleBulkAction(action: string) {
  if (action !== 'delete_selected' || selectedRoleIds.value.length === 0) return
  if (!window.confirm(t('roles.bulkDeleteConfirm', { count: selectedRoleIds.value.length }))) return
  await resourceAdapter.bulkRemove(selectedRoleIds.value); selectedRoleIds.value = []; await loadRoles()
}

onMounted(async () => {
  await Promise.all([loadRoles(), loadResourceManifest('roles').then((manifest) => { roleManifest.value = manifest }).catch(() => { roleManifest.value = null })])
})
</script>

<template>
  <ResourcePageShell :eyebrow="t('nav.manage')" :title="t('roles.title')" :description="t('roles.description')" :refresh-label="t('roles.refresh')" :create-label="t('roles.create')" :create-visible="!formOpen" :error="error" :error-title="t('roles.loadFailed')" :error-description="t('roles.loadFailed')" :loading="loading" @refresh="loadRoles" @create="formOpen = true">
    <Card v-if="formOpen"><CardHeader><CardTitle>{{ t('roles.create') }}</CardTitle><CardDescription>{{ t('roles.createDescription') }}</CardDescription></CardHeader><CardContent><ResourceForm v-if="roleManifest" v-model="form" :manifest="roleManifest" :submitting="submitting" :error-key="formError" translation-namespace="roles" :submit-label="submitting ? t('roles.creating') : t('roles.save')" :cancel-label="t('roles.cancel')" @submit="submitRole" @cancel="formOpen = false; resetForm()" /></CardContent></Card>
    <section class="grid gap-3"><div class="flex items-center justify-between"><div class="flex items-center gap-2"><ShieldCheck aria-hidden="true" /><h2 class="text-lg font-semibold">{{ t('roles.title') }}</h2></div><p class="text-sm text-muted-foreground">{{ t('roles.total', { count: total }) }}</p></div><ResourceQueryBar v-if="roleManifest" v-model:search="search" :sort-by="sortBy" :sort-order="sortOrder" :manifest="roleManifest" :search-placeholder="t('roles.searchPlaceholder')" label-namespace="roles" @update:sort-by="setSort($event, sortOrder)" @update:sort-order="setSort(sortBy, $event)" @submit="applyFilters" /><ResourceTable v-if="roleManifest" :manifest="roleManifest" :rows="roleRows" :permissions="currentUser?.permissions ?? []" selectable @selection-change="selectedRoleIds = $event" @bulk-action="handleRoleBulkAction($event)" :loading="loading" :empty-label="t('roles.empty')" label-namespace="roles"><template #actions="{ row }"><div class="grid justify-items-end gap-2"><ResourceActionBar :manifest="roleManifest" :permissions="currentUser?.permissions ?? []" @action="handleRoleAction(asRole(row), $event)" /><div class="flex max-w-md flex-wrap justify-end gap-2"><Badge variant="secondary">{{ t(`roles.scope.${asRole(row).data_scope ?? 'all'}`) }}</Badge><Badge v-for="permission in permissionsFor(row).slice(0, 4)" :key="permission" variant="outline">{{ permission }}</Badge><Badge v-if="permissionsFor(row).length > 4" variant="outline">+{{ permissionsFor(row).length - 4 }}</Badge></div></div></template></ResourceTable><div v-if="total > pageSize" class="flex items-center justify-between border-t pt-3 text-sm"><span class="text-muted-foreground">{{ t('roles.page', { page, pages: totalPages() }) }}</span><div class="flex gap-2"><Button variant="outline" size="sm" :disabled="loading || page <= 1" @click="changePage(page - 1)">{{ t('roles.previous') }}</Button><Button variant="outline" size="sm" :disabled="loading || page >= totalPages()" @click="changePage(page + 1)">{{ t('roles.next') }}</Button></div></div></section>
  </ResourcePageShell>
  <Sheet v-model:open="detailsOpen"><SheetContent class="w-full overflow-y-auto sm:max-w-xl"><SheetHeader><SheetTitle>{{ t('roles.detailsTitle') }}</SheetTitle><SheetDescription>{{ t('roles.detailsDescription') }}</SheetDescription></SheetHeader><div v-if="selectedRole" class="grid gap-6 px-6 pb-6"><section class="grid gap-4"><div class="grid gap-2"><label for="role-details-name" class="text-sm font-medium">{{ t('roles.name') }}</label><Input id="role-details-name" v-model="detailsForm.name" /></div><div class="grid gap-2"><label for="role-details-description" class="text-sm font-medium">{{ t('roles.descriptionField') }}</label><Textarea id="role-details-description" v-model="detailsForm.description" /></div></section><section class="grid gap-3 border-t pt-5"><div class="flex items-center justify-between"><div><h3 class="font-medium">{{ t('roles.dataScope') }}</h3><p class="text-sm text-muted-foreground">{{ t('roles.dataScopeDescription') }}</p></div><div class="flex gap-2"><Button size="sm" :variant="detailsScope === 'all' ? 'default' : 'outline'" @click="detailsScope = 'all'">{{ t('roles.scope.all') }}</Button><Button size="sm" :variant="detailsScope === 'self' ? 'default' : 'outline'" @click="detailsScope = 'self'">{{ t('roles.scope.self') }}</Button></div></div></section><section class="grid gap-3 border-t pt-5"><div class="flex items-center justify-between gap-3"><div><h3 class="font-medium">{{ t('roles.permissionsTitle') }}</h3><p class="text-sm text-muted-foreground">{{ isAdministrator ? t('roles.administratorAllPermissions') : t('roles.permissionsDescription') }}</p></div><Badge variant="secondary">{{ selectedPermissionCodes.length }} / {{ permissions.length }}</Badge></div><div class="flex flex-wrap gap-2"><Button size="sm" variant="outline" :disabled="isAdministrator" @click="selectAllVisible">{{ t('roles.selectAll') }}</Button><Button size="sm" variant="ghost" :disabled="isAdministrator" @click="clearVisible">{{ t('roles.clearAll') }}</Button><div class="relative min-w-40 flex-1"><Search class="absolute left-2 top-2.5 size-4 text-muted-foreground" aria-hidden="true" /><Input v-model="permissionSearch" class="pl-8" :placeholder="t('roles.permissionSearch')" /></div></div><div class="grid max-h-80 gap-3 overflow-y-auto rounded-lg border p-3"><div v-for="group in permissionGroups" :key="group.name" class="grid gap-2"><button type="button" class="flex items-center justify-between text-left font-medium hover:text-primary disabled:cursor-not-allowed" :disabled="isAdministrator" @click="toggleGroup(group)"><span>{{ group.name }}</span><span class="text-xs text-muted-foreground">{{ group.items.filter((item) => isSelected(item.code)).length }} / {{ group.items.length }}</span></button><label v-for="permission in group.items" :key="permission.id" class="flex cursor-pointer items-start gap-3 rounded-md px-2 py-2 text-sm hover:bg-muted"><input type="checkbox" class="mt-1 size-4 accent-primary" :checked="isSelected(permission.code)" :disabled="isAdministrator" @change="togglePermission(permission.code)" /><span><span class="block font-mono text-xs">{{ permission.code }}</span><span v-if="permission.description" class="text-muted-foreground">{{ permission.description }}</span></span></label></div><p v-if="!permissionGroups.length" class="py-6 text-center text-sm text-muted-foreground">{{ t('roles.noMatchingPermissions') }}</p></div></section><p v-if="detailsError" class="text-sm text-destructive" role="alert">{{ t('roles.detailsSaveFailed') }}</p></div><SheetFooter class="border-t px-6 py-4"><Button variant="outline" @click="closeDetails">{{ t('roles.cancel') }}</Button><Button :disabled="detailsSaving" @click="saveDetails"><Check data-icon="inline-start" aria-hidden="true" />{{ detailsSaving ? t('roles.savingDetails') : t('roles.saveDetails') }}</Button></SheetFooter></SheetContent></Sheet>
</template>
