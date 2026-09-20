<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { ResourceField, ResourceManifest } from '@/core/resources/types'

const props = defineProps<{
  manifest: ResourceManifest
  modelValue: Record<string, string>
  mode?: 'create' | 'edit'
  submitting?: boolean
  errorKey?: string | null
  submitLabel: string
  cancelLabel: string
  translationNamespace?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: Record<string, string>]
  submit: []
  cancel: []
}>()

const { t } = useI18n()
const fields = computed(() => props.manifest.fields.filter((field) => !field.readonly && field.type !== 'boolean'))

function valueFor(field: ResourceField): string {
  return props.modelValue[field.name] ?? ''
}

function update(field: ResourceField, value: string | number) {
  emit('update:modelValue', { ...props.modelValue, [field.name]: String(value) })
}
</script>

<template>
  <form class="grid gap-4 md:grid-cols-3" @submit.prevent="emit('submit')">
    <div v-for="field in fields" :key="field.name" class="grid gap-2">
      <label :for="`resource-${field.name}`" class="text-sm font-medium">{{ t(field.label) }}</label>
      <Input :id="`resource-${field.name}`" :model-value="valueFor(field)" :type="field.type === 'password' ? 'password' : field.type" :required="field.required" :autocomplete="field.type === 'password' ? 'new-password' : 'off'" @update:model-value="update(field, $event)" />
    </div>
    <div class="flex gap-2 md:col-span-3">
      <Button type="submit" :disabled="submitting">{{ submitLabel }}</Button>
      <Button type="button" variant="outline" @click="emit('cancel')">{{ cancelLabel }}</Button>
    </div>
    <p v-if="errorKey" class="text-sm text-destructive md:col-span-3">{{ t(`${props.translationNamespace ?? 'users'}.${errorKey}`) }}</p>
  </form>
</template>
