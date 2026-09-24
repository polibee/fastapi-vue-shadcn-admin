<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Copy, Eye, EyeOff, RefreshCw } from '@lucide/vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import type { ResourceField, ResourceManifest } from '@/core/resources/types'
import { generateSecurePassword } from '@/core/security/password'

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
const passwordVisible = ref(false)
const copiedPassword = ref(false)
const fields = computed(() => props.manifest.fields.filter((field) => !field.readonly && field.type !== 'boolean'))

function valueFor(field: ResourceField): string {
  return props.modelValue[field.name] ?? ''
}

function update(field: ResourceField, value: string | number) {
  emit('update:modelValue', { ...props.modelValue, [field.name]: String(value) })
}

function generatePassword(field: ResourceField): void {
  update(field, generateSecurePassword())
  passwordVisible.value = true
}

async function copyPassword(field: ResourceField): Promise<void> {
  const value = valueFor(field)
  if (!value) return
  await navigator.clipboard.writeText(value)
  copiedPassword.value = true
  window.setTimeout(() => { copiedPassword.value = false }, 1500)
}
</script>

<template>
  <form class="grid gap-4 md:grid-cols-3" @submit.prevent="emit('submit')">
    <div v-for="field in fields" :key="field.name" class="grid gap-2">
      <label :for="`resource-${field.name}`" class="text-sm font-medium">{{ t(field.label) }}</label>
      <div v-if="field.type === 'password'" class="grid gap-2">
        <div class="flex gap-2">
          <Input :id="`resource-${field.name}`" class="min-w-0" :model-value="valueFor(field)" :type="passwordVisible ? 'text' : 'password'" :required="field.required" autocomplete="new-password" @update:model-value="update(field, $event)" />
          <Button type="button" variant="outline" size="icon" :aria-label="t(passwordVisible ? 'common.hide' : 'common.show')" @click="passwordVisible = !passwordVisible"><EyeOff v-if="passwordVisible" aria-hidden="true" /><Eye v-else aria-hidden="true" /></Button>
        </div>
        <div class="flex flex-wrap gap-2">
          <Button type="button" variant="secondary" size="sm" @click="generatePassword(field)"><RefreshCw data-icon="inline-start" aria-hidden="true" />{{ t('common.generate') }}</Button>
          <Button type="button" variant="ghost" size="sm" :disabled="!valueFor(field)" @click="copyPassword(field)"><Copy data-icon="inline-start" aria-hidden="true" />{{ t(copiedPassword ? 'common.copied' : 'common.copy') }}</Button>
        </div>
      </div>
      <Input v-else :id="`resource-${field.name}`" :model-value="valueFor(field)" :type="field.type" :required="field.required" autocomplete="off" @update:model-value="update(field, $event)" />
    </div>
    <div class="flex gap-2 md:col-span-3">
      <Button type="submit" :disabled="submitting">{{ submitLabel }}</Button>
      <Button type="button" variant="outline" @click="emit('cancel')">{{ cancelLabel }}</Button>
    </div>
    <p v-if="errorKey" class="text-sm text-destructive md:col-span-3">{{ t(`${props.translationNamespace ?? 'users'}.${errorKey}`) }}</p>
  </form>
</template>
