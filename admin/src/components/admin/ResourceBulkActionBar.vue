<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import type { ResourceBulkAction } from '@/core/resources/types'

const props = defineProps<{
  actions: ResourceBulkAction[]
  permissions: string[]
  selectedCount: number
}>()

const emit = defineEmits<{ action: [name: string] }>()
const { t } = useI18n()
const visibleActions = () => props.actions.filter((action) => props.permissions.includes(action.permission))
</script>

<template>
  <div v-if="selectedCount > 0 && visibleActions().length" class="flex flex-wrap items-center gap-2 rounded-md border bg-muted/30 p-2">
    <span class="text-sm text-muted-foreground">{{ selectedCount }}</span>
    <Button v-for="action in visibleActions()" :key="action.name" size="sm" variant="outline" @click="emit('action', action.name)">{{ t(action.label) }}</Button>
  </div>
</template>
