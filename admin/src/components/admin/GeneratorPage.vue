<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { FileCode2, RefreshCw, Sparkles } from '@lucide/vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { fetchCrudGenerationPlan, type CrudGenerationPlan } from '@/core/api/generator'
import { fetchHealth, type HealthStatus } from '@/core/api/health'
import { loadResourceIndex } from '@/core/resources'
import type { ResourceManifest } from '@/core/resources/types'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const manifests = ref<ResourceManifest[]>([])
const selectedResource = ref('')
const plan = ref<CrudGenerationPlan | null>(null)
const loading = ref(false)
const error = ref(false)
const healthStatus = ref<HealthStatus>('unavailable')

async function loadPlan(resource: string) {
  selectedResource.value = resource
  loading.value = true
  error.value = false
  try {
    plan.value = await fetchCrudGenerationPlan(resource)
  } catch {
    error.value = true
    plan.value = null
  } finally {
    loading.value = false
  }
}

async function loadResources() {
  try {
    const [resourceResult, health] = await Promise.all([loadResourceIndex(), fetchHealth()])
    manifests.value = resourceResult
    healthStatus.value = health.status
    if (manifests.value[0]) await loadPlan(manifests.value[0].name)
  } catch {
    error.value = true
  }
}

onMounted(loadResources)
</script>

<template>
  <AdminShell :system-status="healthStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end"><div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ t('nav.manage') }}</p><h1 class="flex items-center gap-2 text-3xl font-semibold tracking-tight"><Sparkles class="size-6" aria-hidden="true" />{{ t('generator.title') }}</h1><p class="text-sm text-muted-foreground">{{ t('generator.description') }}</p></div><Badge variant="outline">{{ t('generator.readOnly') }}</Badge></section>
      <div class="flex flex-wrap gap-2" role="tablist" :aria-label="t('generator.selectResource')"><Button v-for="manifest in manifests" :key="manifest.name" :variant="selectedResource === manifest.name ? 'default' : 'outline'" role="tab" :aria-selected="selectedResource === manifest.name" @click="loadPlan(manifest.name)">{{ t(manifest.labelPlural) }}</Button></div>
      <p v-if="loading" class="text-sm text-muted-foreground" role="status">{{ t('generator.loading') }}</p>
      <p v-if="error" class="rounded-md border border-destructive/50 p-4 text-sm text-destructive" role="alert">{{ t('generator.loadError') }}</p>
      <Card v-if="plan"><CardHeader><CardTitle>{{ t('generator.plan') }} · {{ plan.resource }}</CardTitle><CardDescription>{{ plan.schemaVersion }} · {{ plan.generatorVersion }}</CardDescription></CardHeader><CardContent class="grid gap-6"><div><p class="text-xs text-muted-foreground">{{ t('generator.module') }}</p><p class="mt-1 font-mono text-sm">{{ plan.module }}</p></div><div><p class="text-xs text-muted-foreground">{{ t('generator.permissions') }}</p><div class="mt-2 flex flex-wrap gap-2"><Badge v-for="permission in plan.permissions" :key="permission" variant="secondary">{{ permission }}</Badge></div></div><div><p class="text-xs text-muted-foreground">{{ t('generator.files') }}</p><div class="mt-2 grid gap-2"> <div v-for="file in plan.files" :key="file.path" class="flex items-center justify-between gap-3 rounded-md border px-3 py-2 text-sm"><span class="flex min-w-0 items-center gap-2"><FileCode2 class="size-4 shrink-0 text-muted-foreground" aria-hidden="true" /><span class="truncate font-mono">{{ file.path }}</span></span><Badge variant="outline">{{ file.overwrite === 'never' ? t('generator.never') : file.overwrite }}</Badge></div></div></div></CardContent></Card>
    </main>
  </AdminShell>
</template>
