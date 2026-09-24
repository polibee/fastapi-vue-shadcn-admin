<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { ArrowLeft, RefreshCw } from '@lucide/vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import AdminShell from './AdminShell.vue'
import { fetchHealth, type HealthStatus } from '@/core/api/health'

withDefaults(defineProps<{
  eyebrow: string
  title: string
  description: string
  backLabel: string
  backTo: string
  refreshLabel: string
  loading?: boolean
  error?: boolean
  errorTitle: string
  errorDescription: string
}>(), { loading: false, error: false })

const emit = defineEmits<{ refresh: [] }>()
const systemStatus = ref<HealthStatus>('unavailable')

onMounted(async () => {
  try { systemStatus.value = (await fetchHealth()).status } catch { systemStatus.value = 'unavailable' }
})
</script>

<template>
  <AdminShell :system-status="systemStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <header class="flex flex-col gap-4 border-b pb-6 md:flex-row md:items-start md:justify-between">
        <div class="grid gap-3">
          <RouterLink :to="backTo" class="inline-flex w-fit items-center gap-2 text-sm text-muted-foreground transition-colors hover:text-foreground">
            <ArrowLeft class="size-4" aria-hidden="true" />{{ backLabel }}
          </RouterLink>
          <div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ eyebrow }}</p><h1 class="text-3xl font-semibold tracking-tight">{{ title }}</h1><p class="max-w-3xl text-sm text-muted-foreground">{{ description }}</p></div>
        </div>
        <Button variant="outline" :disabled="loading" @click="emit('refresh')"><RefreshCw data-icon="inline-start" :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ refreshLabel }}</Button>
      </header>
      <Alert v-if="error" variant="destructive"><AlertTitle>{{ errorTitle }}</AlertTitle><AlertDescription>{{ errorDescription }}</AlertDescription></Alert>
      <slot />
    </main>
  </AdminShell>
</template>
