<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Check, Search, ShieldCheck } from '@lucide/vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { fetchRole, updateRole } from '@/core/api/resources'
import { loadPermissions } from '@/core/api/permissions'
import { groupPermissions, type PermissionGroup } from '@/core/permissions/catalog'
import type { PermissionRead, RoleRead } from '@/core/api/generated/client'
import ResourceDetailPageShell from './ResourceDetailPageShell.vue'
import { adminPath } from '@/router/paths'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const role = ref<RoleRead | null>(null)
const permissions = ref<PermissionRead[]>([])
const name = ref('')
const description = ref('')
const dataScope = ref<'all' | 'self'>('all')
const selectedCodes = ref<string[]>([])
const permissionSearch = ref('')
const loading = ref(true)
const saving = ref(false)
const error = ref(false)
const permissionGroups = computed<PermissionGroup[]>(() => groupPermissions(permissions.value).map((group) => ({ ...group, name: t(`roles.permissionGroups.${group.name}`), items: group.items.filter((item) => item.code.toLowerCase().includes(permissionSearch.value.toLowerCase())) })).filter((group) => group.items.length))
const visibleCodes = computed(() => permissionGroups.value.flatMap((group) => group.items.map((item) => item.code)))
const administrator = computed(() => role.value?.name === 'administrator')
const selectedCount = computed(() => selectedCodes.value.length)

function isSelected(code: string) { return selectedCodes.value.includes(code) }
function togglePermission(code: string) { if (!administrator.value) selectedCodes.value = isSelected(code) ? selectedCodes.value.filter((item) => item !== code) : [...selectedCodes.value, code] }
function toggleGroup(group: PermissionGroup) { if (administrator.value) return; const codes = group.items.map((item) => item.code); const all = codes.every(isSelected); selectedCodes.value = all ? selectedCodes.value.filter((code) => !codes.includes(code)) : [...new Set([...selectedCodes.value, ...codes])] }
function selectVisible() { if (!administrator.value) selectedCodes.value = [...new Set([...selectedCodes.value, ...visibleCodes.value])] }
function clearVisible() { if (!administrator.value) selectedCodes.value = selectedCodes.value.filter((code) => !visibleCodes.value.includes(code)) }

async function loadDetails() {
  loading.value = true; error.value = false
  try {
    const id = Number(route.params.id)
    const [loadedRole, permissionResult] = await Promise.all([fetchRole(id), loadPermissions()])
    role.value = loadedRole; name.value = loadedRole.name; description.value = loadedRole.description ?? ''; dataScope.value = loadedRole.data_scope ?? 'all'; permissions.value = permissionResult.items; selectedCodes.value = loadedRole.name === 'administrator' ? permissionResult.items.map((item) => item.code) : [...loadedRole.permissions]
  } catch { error.value = true } finally { loading.value = false }
}

async function save() {
  if (!role.value) return
  saving.value = true; error.value = false
  try { await updateRole(role.value.id, { name: name.value, description: description.value, data_scope: dataScope.value, permissions: selectedCodes.value }); await loadDetails() } catch { error.value = true } finally { saving.value = false }
}

onMounted(loadDetails)
</script>

<template>
  <ResourceDetailPageShell :eyebrow="t('nav.manage')" :title="role?.name || t('roles.detailsTitle')" :description="t('roles.detailsDescription')" :back-label="t('roles.backToList')" :back-to="adminPath('/roles')" :refresh-label="t('roles.refresh')" :loading="loading" :error="error" :error-title="t('roles.detailsLoadFailed')" :error-description="t('roles.detailsLoadFailed')" @refresh="loadDetails">
    <div v-if="loading" class="rounded-xl border border-dashed p-12 text-center text-sm text-muted-foreground">{{ t('roles.loading') }}</div>
    <div v-else-if="role" class="grid gap-6 xl:grid-cols-[minmax(0,1fr)_20rem]">
      <div class="grid gap-6">
        <Card><CardHeader><CardTitle>{{ t('roles.basicInformation') }}</CardTitle><CardDescription>{{ t('roles.basicInformationDescription') }}</CardDescription></CardHeader><CardContent class="grid gap-5 md:grid-cols-2"><div class="grid gap-2"><label for="role-name" class="text-sm font-medium">{{ t('roles.name') }}</label><Input id="role-name" v-model="name" /></div><div class="grid gap-2 md:col-span-2"><label for="role-description" class="text-sm font-medium">{{ t('roles.descriptionField') }}</label><Textarea id="role-description" v-model="description" /></div></CardContent></Card>
        <Card><CardHeader><div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between"><div><CardTitle>{{ t('roles.permissionsTitle') }}</CardTitle><CardDescription>{{ administrator ? t('roles.administratorAllPermissions') : t('roles.permissionsDescription') }}</CardDescription></div><Badge variant="secondary">{{ selectedCount }} / {{ permissions.length }}</Badge></div></CardHeader><CardContent class="grid gap-5"><div class="flex flex-col gap-3 rounded-lg bg-muted/40 p-3 sm:flex-row sm:items-center"><Button size="sm" variant="outline" :disabled="administrator" @click="selectVisible">{{ t('roles.selectAll') }}</Button><Button size="sm" variant="ghost" :disabled="administrator" @click="clearVisible">{{ t('roles.clearAll') }}</Button><div class="relative min-w-0 flex-1"><Search class="absolute left-2 top-2.5 size-4 text-muted-foreground" aria-hidden="true" /><Input v-model="permissionSearch" class="pl-8" :placeholder="t('roles.permissionSearch')" /></div></div><div class="grid gap-4 md:grid-cols-2"><fieldset v-for="group in permissionGroups" :key="group.name" class="rounded-xl border p-4"><legend class="px-2 text-sm font-semibold">{{ group.name }} <span class="font-normal text-muted-foreground">({{ group.items.filter((item) => isSelected(item.code)).length }}/{{ group.items.length }})</span></legend><div class="grid gap-2"><label v-for="permission in group.items" :key="permission.id" class="flex cursor-pointer items-start gap-3 rounded-lg p-2 text-sm transition-colors hover:bg-muted"><input type="checkbox" class="mt-1 size-4 accent-primary" :checked="isSelected(permission.code)" :disabled="administrator" @change="togglePermission(permission.code)" /><span class="min-w-0"><span class="block break-all font-mono text-xs">{{ permission.code }}</span><span v-if="permission.description" class="block text-muted-foreground">{{ permission.description }}</span></span></label></div><button type="button" class="mt-3 text-xs text-muted-foreground hover:text-foreground disabled:cursor-not-allowed" :disabled="administrator" @click="toggleGroup(group)">{{ t('roles.toggleGroup') }}</button></fieldset></div><p v-if="!permissionGroups.length" class="py-6 text-center text-sm text-muted-foreground">{{ t('roles.noMatchingPermissions') }}</p></CardContent></Card>
      </div>
      <aside class="grid content-start gap-6"><Card><CardHeader><CardTitle class="flex items-center gap-2"><ShieldCheck class="size-5" aria-hidden="true" />{{ t('roles.roleSummary') }}</CardTitle></CardHeader><CardContent class="grid gap-4 text-sm"><div><p class="text-muted-foreground">{{ t('roles.dataScope') }}</p><div class="mt-2 flex gap-2"><Button size="sm" :variant="dataScope === 'all' ? 'default' : 'outline'" @click="dataScope = 'all'">{{ t('roles.scope.all') }}</Button><Button size="sm" :variant="dataScope === 'self' ? 'default' : 'outline'" @click="dataScope = 'self'">{{ t('roles.scope.self') }}</Button></div></div><div class="border-t pt-4"><p class="text-muted-foreground">{{ t('roles.permissionCount') }}</p><p class="mt-1 text-2xl font-semibold">{{ selectedCount }}</p></div><div v-if="administrator" class="rounded-lg border border-primary/20 bg-primary/5 p-3 text-xs text-muted-foreground">{{ t('roles.administratorAllPermissions') }}</div></CardContent></Card><div class="sticky bottom-4 flex gap-2 rounded-xl border bg-background/95 p-3 shadow-lg backdrop-blur"><Button class="flex-1" variant="outline" @click="router.push(adminPath('/roles'))">{{ t('roles.cancel') }}</Button><Button class="flex-1" :disabled="saving" @click="save"><Check data-icon="inline-start" aria-hidden="true" />{{ saving ? t('roles.savingDetails') : t('roles.saveDetails') }}</Button></div></aside>
    </div>
  </ResourceDetailPageShell>
</template>
