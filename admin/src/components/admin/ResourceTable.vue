<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Card, CardContent } from '@/components/ui/card'
import type { ResourceManifest } from '@/core/resources/types'
import ResourceCell from './ResourceCell.vue'
import ResourceActionBar from './ResourceActionBar.vue'
import ResourceBulkActionBar from './ResourceBulkActionBar.vue'
import { useResourceSelection } from '@/core/resources/selection'

const props = defineProps<{
  manifest: ResourceManifest
  rows: Array<Record<string, unknown>>
  loading?: boolean
  emptyLabel: string
  labelNamespace?: string
  permissions?: string[]
  selectable?: boolean
}>()
const emit = defineEmits<{ action: [row: Record<string, unknown>, name: string]; bulkAction: [name: string]; selectionChange: [ids: number[]] }>()

const { t } = useI18n()
const fields = computed(() => props.manifest.table.columns.map((name) => props.manifest.fields.find((field) => field.name === name)).filter((field): field is ResourceManifest['fields'][number] => Boolean(field)))
const labelNamespace = computed(() => props.labelNamespace ?? props.manifest.name)
const { selectedIds, toggle, toggleAll: selectAll } = useResourceSelection()
function rowId(row: Record<string, unknown>, index: number): number | null { return typeof row.id === 'number' ? row.id : index }
function toggleRow(row: Record<string, unknown>, index: number) {
  const id = rowId(row, index)
  if (id === null) return
  toggle(id)
  emit('selectionChange', selectedIds.value)
}
function toggleAll() {
  selectAll(props.rows.map((row, index) => rowId(row, index)).filter((id): id is number => id !== null))
  emit('selectionChange', selectedIds.value)
}
</script>

<template>
  <Card>
    <CardContent class="grid gap-3 overflow-x-auto p-0">
      <ResourceBulkActionBar v-if="selectable" :actions="manifest.bulkActions" :permissions="permissions ?? []" :selected-count="selectedIds.length" class="mx-4 mt-4" @action="emit('bulkAction', $event)" />
      <div v-if="!loading && rows.length === 0" class="p-8 text-center text-sm text-muted-foreground">{{ emptyLabel }}</div>
      <table v-else class="w-full text-sm">
        <caption class="sr-only">{{ t(`${labelNamespace}.title`) }}</caption>
        <thead class="border-b text-left text-muted-foreground"><tr><th v-if="selectable" scope="col" class="h-11 w-10 px-4"><input type="checkbox" :checked="selectedIds.length === rows.length && rows.length > 0" :aria-label="t('common.selectAll')" @change="toggleAll" /></th><th v-for="field in fields" :key="field.name" scope="col" class="h-11 px-4 font-medium">{{ t(field.label) }}</th><th scope="col" class="h-11 px-4 text-right font-medium"><span class="sr-only">{{ t('common.actions') }}</span></th></tr></thead>
        <tbody><tr v-for="(row, index) in rows" :key="String(row.id ?? index)" class="border-b last:border-0"><td v-if="selectable" class="p-4 align-middle"><input type="checkbox" :checked="selectedIds.includes(rowId(row, index) ?? -1)" :aria-label="`${t('common.select')} ${row.id ?? index}`" @change="toggleRow(row, index)" /></td><td v-for="field in fields" :key="field.name" class="p-4 align-middle"><slot :name="`cell-${field.name}`" :row="row" :value="row[field.name]"><ResourceCell :field="field" :value="row[field.name]" :namespace="labelNamespace" /></slot></td><td class="p-4 text-right align-middle"><slot name="actions" :row="row"><ResourceActionBar :manifest="manifest" :permissions="permissions ?? []" @action="emit('action', row, $event)" /></slot></td></tr></tbody>
      </table>
    </CardContent>
  </Card>
</template>
