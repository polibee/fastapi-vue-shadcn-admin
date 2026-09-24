<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus } from '@lucide/vue'
import ResourceForm from './ResourceForm.vue'
import ResourcePageShell from './ResourcePageShell.vue'
import ResourceQueryBar from './ResourceQueryBar.vue'
import ResourceTable from './ResourceTable.vue'
import { loadResourceManifest } from '@/core/resources'
import type { ResourceManifest } from '@/core/resources/types'
import { resourceAdapterRegistry } from '@/core/resources/adapters'
import { validateResourceForm } from '@/core/resources/validation'
import { currentUser, ensureCurrentUser } from '@/core/permissions'
import { useRouter } from 'vue-router'
import { adminPath } from '@/router/paths'

const props = defineProps<{ resourceName: string; namespace: string }>()
const { t } = useI18n()
const router = useRouter()
const manifest = ref<ResourceManifest | null>(null)
const rows = ref<Array<Record<string, any>>>([])
const total = ref(0)
const page = ref(1)
const pageSize = 10
const sortBy = ref('id')
const sortOrder = ref<'asc' | 'desc'>('asc')
const search = ref('')
const filters = ref<Record<string, boolean | undefined>>({})
const loading = ref(false)
const error = ref(false)
const formOpen = ref(false)
const editing = ref<Record<string, any> | null>(null)
const form = ref<Record<string, string>>({})
const formError = ref<string | null>(null)
const submitting = ref(false)
const selectedIds = ref<number[]>([])

const adapter = computed(() => resourceAdapterRegistry.get<any, any>(props.resourceName))
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const title = computed(() => t(`${props.namespace}.title`))
const isEdit = computed(() => Boolean(editing.value))

function resetForm(): void { form.value = {}; formError.value = null; editing.value = null }
function openCreate(): void { resetForm(); formOpen.value = true }
function openEdit(row: Record<string, any>): void {
  editing.value = row
  form.value = Object.fromEntries(Object.entries(row).filter(([, value]) => typeof value !== 'boolean' && value !== null).map(([key, value]) => [key, String(value)]))
  formError.value = null
  formOpen.value = true
}
function closeForm(): void { formOpen.value = false; resetForm() }
async function load(): Promise<void> {
  if (!manifest.value) return
  loading.value = true; error.value = false
  try {
    const result = await adapter.value.list({ offset: (page.value - 1) * pageSize, limit: pageSize, search: search.value || undefined, isActive: filters.value.is_active, sortBy: sortBy.value, sortOrder: sortOrder.value })
    rows.value = result.items as Array<Record<string, any>>; total.value = result.total
  } catch { error.value = true } finally { loading.value = false }
}
async function applyFilters(): Promise<void> { page.value = 1; await load() }
async function changeSort(field: string, order: 'asc' | 'desc'): Promise<void> { sortBy.value = field; sortOrder.value = order; await applyFilters() }
async function save(): Promise<void> {
  if (!manifest.value) return
  formError.value = validateResourceForm(manifest.value, form.value)
  if (formError.value) return
  submitting.value = true
  try {
    const values: Record<string, any> = { ...form.value }
    if (editing.value) { values.id = editing.value.id; values.is_active = editing.value.is_active; await adapter.value.update?.(editing.value.id, values) }
    else { values.is_active = true; await adapter.value.create(values) }
    closeForm(); await load()
  } catch { formError.value = isEdit.value ? 'updateFailed' : 'createFailed' } finally { submitting.value = false }
}
async function remove(row: Record<string, any>): Promise<void> {
  if (!window.confirm(t(`${props.namespace}.deleteConfirm`, { name: row.name }))) return
  try { await adapter.value.remove(row.id); await load() } catch { error.value = true }
}
async function handleAction(row: Record<string, any>, action: string): Promise<void> { if (action === 'edit') void router.push(adminPath(`/${props.resourceName}/${row.id}`)); if (action === 'delete') await remove(row) }
async function handleBulkAction(action: string): Promise<void> {
  if (action !== 'delete_selected' || selectedIds.value.length === 0) return
  if (!window.confirm(t(`${props.namespace}.bulkDeleteConfirm`, { count: selectedIds.value.length }))) return
  await adapter.value.bulkRemove(selectedIds.value); selectedIds.value = []; await load()
}

onMounted(async () => {
  await ensureCurrentUser()
  manifest.value = await loadResourceManifest(props.resourceName)
  sortBy.value = manifest.value.query.defaultSort.field
  sortOrder.value = manifest.value.query.defaultSort.direction
  await load()
})
</script>

<template>
  <ResourcePageShell :eyebrow="t('nav.manage')" :title="title" :description="t(`${namespace}.description`)" :refresh-label="t(`${namespace}.refresh`)" :create-label="t(`${namespace}.create`)" :create-visible="!formOpen && currentUser?.permissions.includes(manifest?.permissions.create ?? '')" :error="error" :error-title="t(`${namespace}.loadFailed`)" :error-description="t(`${namespace}.loadFailed`)" :loading="loading" @refresh="load" @create="openCreate">
    <Card v-if="formOpen && manifest">
      <CardHeader><CardTitle>{{ t(isEdit ? `${namespace}.edit` : `${namespace}.create`) }}</CardTitle></CardHeader>
      <CardContent><ResourceForm v-model="form" :manifest="manifest" :submitting="submitting" :error-key="formError" :translation-namespace="namespace" :submit-label="t(submitting ? `${namespace}.saving` : `${namespace}.save`)" :cancel-label="t(`${namespace}.cancel`)" @submit="save" @cancel="closeForm" /></CardContent>
    </Card>
    <section v-if="manifest" class="grid gap-3">
      <ResourceQueryBar v-model:search="search" v-model:filters="filters" :sort-by="sortBy" :sort-order="sortOrder" :manifest="manifest" :search-placeholder="t(`${namespace}.searchPlaceholder`)" :label-namespace="namespace" @update:sort-by="changeSort($event, sortOrder)" @update:sort-order="changeSort(sortBy, $event)" @submit="applyFilters" />
      <ResourceTable :manifest="manifest" :rows="rows" :permissions="currentUser?.permissions ?? []" selectable :loading="loading" :empty-label="t(`${namespace}.empty`)" :label-namespace="namespace" @selection-change="selectedIds = $event" @action="handleAction" @bulk-action="handleBulkAction" />
      <div v-if="total > pageSize" class="flex items-center justify-between border-t pt-3 text-sm"><span class="text-muted-foreground">{{ t(`${namespace}.page`, { page, pages: totalPages }) }}</span><div class="flex gap-2"><Button variant="outline" size="sm" :disabled="loading || page <= 1" @click="page--; load()">{{ t('common.previous') }}</Button><Button variant="outline" size="sm" :disabled="loading || page >= totalPages" @click="page++; load()">{{ t('common.next') }}</Button></div></div>
    </section>
  </ResourcePageShell>
</template>
