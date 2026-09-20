<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { KeyRound, RefreshCw } from '@lucide/vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { loadPermissions } from '@/core/api/permissions'
import { fetchHealth, type HealthStatus } from '@/core/api/health'
import type { PermissionRead } from '@/core/api/generated/client'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const items = ref<PermissionRead[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref(false)
const healthStatus = ref<HealthStatus>('unavailable')

async function load() {
  loading.value = true
  error.value = false
  try {
    const [result, health] = await Promise.all([loadPermissions(), fetchHealth()])
    items.value = result.items
    total.value = result.total
    healthStatus.value = health.status
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <AdminShell :system-status="healthStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end"><div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ t('nav.manage') }}</p><h1 class="flex items-center gap-2 text-3xl font-semibold tracking-tight"><KeyRound class="size-6" aria-hidden="true" />{{ t('permissions.title') }}</h1><p class="text-sm text-muted-foreground">{{ t('permissions.description') }}</p></div><Button variant="outline" :disabled="loading" @click="load"><RefreshCw :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ t('permissions.refresh') }}</Button></section>
      <p v-if="error" class="rounded-md border border-destructive/50 p-4 text-sm text-destructive" role="alert">{{ t('permissions.loadError') }}</p>
      <Card><CardHeader><CardTitle>{{ t('permissions.catalog') }}</CardTitle><CardDescription>{{ t('permissions.total', { count: total }) }}</CardDescription></CardHeader><CardContent><div v-if="items.length" class="grid gap-3 md:grid-cols-2"><div v-for="permission in items" :key="permission.id" class="flex items-start justify-between gap-4 rounded-md border p-4"><div class="min-w-0"><p class="break-all font-mono text-sm font-medium">{{ permission.code }}</p><p class="mt-1 text-sm text-muted-foreground">{{ permission.description || t('permissions.noDescription') }}</p></div><Badge variant="outline">{{ t('permissions.registered') }}</Badge></div></div><p v-else-if="!loading" class="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">{{ t('permissions.empty') }}</p><p v-if="loading" class="p-8 text-center text-sm text-muted-foreground" role="status">{{ t('permissions.loading') }}</p></CardContent></Card>
    </main>
  </AdminShell>
</template>
