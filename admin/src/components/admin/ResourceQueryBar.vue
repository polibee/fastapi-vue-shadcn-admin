<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { ResourceManifest } from '@/core/resources/types'

const props = withDefaults(defineProps<{
  manifest: ResourceManifest
  search: string
  sortBy: string
  sortOrder: 'asc' | 'desc'
  filters?: Record<string, boolean | undefined>
  labelNamespace?: string
  searchPlaceholder: string
}>(), { filters: () => ({}), labelNamespace: undefined })

const emit = defineEmits<{
  'update:search': [value: string]
  'update:sortBy': [value: string]
  'update:sortOrder': [value: 'asc' | 'desc']
  'update:filters': [value: Record<string, boolean | undefined>]
  submit: []
}>()

const { t } = useI18n()
const namespace = computed(() => props.labelNamespace ?? props.manifest.name)
const filterFields = computed(() => props.manifest.query.filterFields.map((name) => props.manifest.fields.find((field) => field.name === name)).filter((field): field is ResourceManifest['fields'][number] => Boolean(field)))
const sortFields = computed(() => props.manifest.query.sortFields.map((name) => props.manifest.fields.find((field) => field.name === name)).filter((field): field is ResourceManifest['fields'][number] => Boolean(field)))

function filterValue(name: string): boolean | undefined {
  return props.filters[name]
}

function setFilter(name: string, value: boolean | undefined): void {
  emit('update:filters', { ...props.filters, [name]: value })
  emit('submit')
}
</script>

<template>
  <form class="grid gap-2 md:grid-cols-[1fr_auto]" @submit.prevent="emit('submit')">
    <Input :model-value="search" :placeholder="searchPlaceholder" :aria-label="searchPlaceholder" @update:model-value="emit('update:search', String($event))" />
    <div v-for="field in filterFields" :key="field.name" class="flex gap-1" role="group" :aria-label="t(field.label)">
      <template v-if="field.type === 'boolean'">
        <Button type="button" size="sm" :variant="filterValue(field.name) === undefined ? 'secondary' : 'outline'" @click="setFilter(field.name, undefined)">{{ t(`${namespace}.allStatuses`) }}</Button>
        <Button type="button" size="sm" :variant="filterValue(field.name) === true ? 'secondary' : 'outline'" @click="setFilter(field.name, true)">{{ t(`${namespace}.active`) }}</Button>
        <Button type="button" size="sm" :variant="filterValue(field.name) === false ? 'secondary' : 'outline'" @click="setFilter(field.name, false)">{{ t(`${namespace}.inactive`) }}</Button>
      </template>
    </div>
    <div v-if="sortFields.length > 0" class="flex gap-2">
      <label class="sr-only" :for="`${manifest.name}-sort-by`">{{ t('common.sortBy') }}</label>
      <select :id="`${manifest.name}-sort-by`" class="h-9 rounded-md border border-input bg-background px-2 text-sm" :value="sortBy" @change="emit('update:sortBy', ($event.target as HTMLSelectElement).value)">
        <option v-for="field in sortFields" :key="field.name" :value="field.name">{{ t(field.label) }}</option>
      </select>
      <label class="sr-only" :for="`${manifest.name}-sort-order`">{{ t('common.sortOrder') }}</label>
      <select :id="`${manifest.name}-sort-order`" class="h-9 rounded-md border border-input bg-background px-2 text-sm" :value="sortOrder" @change="emit('update:sortOrder', ($event.target as HTMLSelectElement).value as 'asc' | 'desc')">
        <option value="asc">{{ t('common.ascending') }}</option>
        <option value="desc">{{ t('common.descending') }}</option>
      </select>
    </div>
    <Button type="submit" variant="outline">{{ t(`${namespace}.search`) }}</Button>
  </form>
</template>
