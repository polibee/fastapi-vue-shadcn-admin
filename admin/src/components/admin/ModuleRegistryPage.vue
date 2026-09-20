<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Package, RefreshCw } from '@lucide/vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { loadResourceIndex } from '@/core/resources'
import { fetchHealth, type HealthStatus } from '@/core/api/health'
import type { ResourceManifest } from '@/core/resources/types'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const manifests = ref<ResourceManifest[]>([])
const loading = ref(false)
const error = ref(false)
const healthStatus = ref<HealthStatus>('unavailable')

async function loadModules() {
  loading.value = true
  error.value = false
  try {
    const [resourceResult, health] = await Promise.all([loadResourceIndex(), fetchHealth()])
    manifests.value = resourceResult
    healthStatus.value = health.status
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadModules)
</script>

<template>
  <AdminShell :system-status="healthStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end"><div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ t('nav.manage') }}</p><h1 class="flex items-center gap-2 text-3xl font-semibold tracking-tight"><Package class="size-6" aria-hidden="true" />{{ t('modules.title') }}</h1><p class="text-sm text-muted-foreground">{{ t('modules.description') }}</p></div><Button variant="outline" :disabled="loading" @click="loadModules"><RefreshCw :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ t('modules.refresh') }}</Button></section>
      <p v-if="error" class="rounded-md border border-destructive/50 p-4 text-sm text-destructive" role="alert">{{ t('modules.loadError') }}</p>
      <p v-if="loading && !manifests.length" class="text-sm text-muted-foreground" role="status">{{ t('modules.loading') }}</p>
      <div v-if="manifests.length" class="grid gap-4 lg:grid-cols-2"><Card v-for="manifest in manifests" :key="manifest.name"><CardHeader><CardTitle>{{ t(manifest.labelPlural) }}</CardTitle><CardDescription>{{ manifest.name }}</CardDescription></CardHeader><CardContent class="grid gap-4 text-sm"><div class="grid gap-2 sm:grid-cols-2"><div><p class="text-xs text-muted-foreground">{{ t('modules.api') }}</p><p class="mt-1 break-all font-mono">{{ manifest.api.base }}</p></div><div><p class="text-xs text-muted-foreground">{{ t('modules.route') }}</p><p class="mt-1 font-mono">{{ manifest.routes.list }}</p></div></div><div><p class="text-xs text-muted-foreground">{{ t('modules.permissions') }}</p><div class="mt-2 flex flex-wrap gap-2"><Badge v-for="permission in Object.values(manifest.permissions)" :key="permission" variant="secondary">{{ permission }}</Badge></div></div><div><p class="text-xs text-muted-foreground">{{ t('modules.fields') }}</p><div class="mt-2 flex flex-wrap gap-2"><Badge v-for="field in manifest.fields" :key="field.name" variant="outline">{{ field.name }}</Badge></div></div><div><p class="text-xs text-muted-foreground">{{ t('modules.features') }}</p><div class="mt-2 flex flex-wrap gap-2"><Badge v-for="(enabled, feature) in manifest.features" :key="feature" variant="outline">{{ feature }}: {{ enabled ? t('modules.enabled') : t('modules.disabled') }}</Badge></div></div></CardContent></Card></div><p v-else-if="!loading" class="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">{{ t('modules.empty') }}</p>
    </main>
  </AdminShell>
</template>
