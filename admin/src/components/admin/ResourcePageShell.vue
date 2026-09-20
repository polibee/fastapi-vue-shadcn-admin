<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { RefreshCw } from '@lucide/vue'
import AdminShell from './AdminShell.vue'
import { fetchHealth, type HealthStatus } from '@/core/api/health'

withDefaults(defineProps<{
  eyebrow: string
  title: string
  description: string
  refreshLabel: string
  createLabel: string
  errorTitle: string
  errorDescription: string
  loading?: boolean
  error?: boolean
  createVisible?: boolean
}>(), { loading: false, error: false, createVisible: true })

const emit = defineEmits<{ refresh: []; create: [] }>()
const systemStatus = ref<HealthStatus>('unavailable')

onMounted(async () => {
  try {
    systemStatus.value = (await fetchHealth()).status
  } catch {
    systemStatus.value = 'unavailable'
  }
})
</script>

<template>
  <AdminShell :system-status="systemStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ eyebrow }}</p><h1 class="text-3xl font-semibold tracking-tight">{{ title }}</h1><p class="text-sm text-muted-foreground">{{ description }}</p></div>
        <div class="flex gap-2"><Button variant="outline" :disabled="loading" @click="emit('refresh')"><RefreshCw data-icon="inline-start" :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ refreshLabel }}</Button><Button v-if="createVisible" @click="emit('create')">{{ createLabel }}</Button></div>
      </section>
      <Alert v-if="error" variant="destructive"><AlertTitle>{{ errorTitle }}</AlertTitle><AlertDescription>{{ errorDescription }}</AlertDescription></Alert>
      <slot />
    </main>
  </AdminShell>
</template>
