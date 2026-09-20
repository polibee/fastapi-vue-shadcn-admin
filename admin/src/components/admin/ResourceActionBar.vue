<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { MoreHorizontal, Pencil, Trash2 } from '@lucide/vue'
import type { Component } from 'vue'
import { Button } from '@/components/ui/button'
import type { ResourceAction, ResourceManifest } from '@/core/resources/types'

const props = defineProps<{
  manifest: ResourceManifest
  permissions: string[]
}>()

const emit = defineEmits<{ action: [name: string] }>()
const { t } = useI18n()

function visible(action: ResourceAction): boolean {
  return props.permissions.includes(action.permission)
}

function label(action: ResourceAction): string {
  return t(action.label)
}

function iconFor(action: ResourceAction): Component {
  if (action.icon === 'edit') return Pencil
  if (action.icon === 'delete') return Trash2
  return MoreHorizontal
}
</script>

<template>
  <div class="flex flex-wrap justify-end gap-1">
    <Button v-for="action in manifest.actions.filter(visible)" :key="action.name" variant="ghost" size="icon" :aria-label="label(action)" @click="emit('action', action.name)">
      <span class="sr-only">{{ label(action) }}</span>
      <component :is="iconFor(action)" aria-hidden="true" />
    </Button>
  </div>
</template>
