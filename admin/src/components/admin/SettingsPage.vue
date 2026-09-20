<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RefreshCw, ShieldCheck } from '@lucide/vue'
import { useI18n } from 'vue-i18n'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { fetchHealth, type HealthStatus, type HealthSummary } from '@/core/api/health'
import { fetchSettings, type RuntimeSettings } from '@/core/api/settings'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const settings = ref<RuntimeSettings | null>(null)
const loading = ref(false)
const error = ref(false)
const health = ref<HealthSummary | null>(null)

async function loadSettings() {
  loading.value = true
  error.value = false
  try {
    const [runtimeSettings, healthSummary] = await Promise.all([fetchSettings(), fetchHealth()])
    settings.value = runtimeSettings
    health.value = healthSummary
  } catch {
    try {
      settings.value = await fetchSettings()
    } catch {
      error.value = true
    }
    health.value = null
  } finally {
    loading.value = false
  }
}

function statusLabel(status: HealthStatus): string {
  if (status === 'ok') return t('settings.operational')
  if (status === 'degraded') return t('settings.degraded')
  return t('settings.unavailable')
}

function configured(value: boolean): string {
  return value ? t('settings.configured') : t('settings.notConfigured')
}

onMounted(loadSettings)
</script>

<template>
  <AdminShell :system-status="health?.status ?? 'unavailable'">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div class="mb-2 flex items-center gap-2">
            <h1 class="text-2xl font-semibold tracking-tight">{{ t('settings.title') }}</h1>
            <Badge variant="outline">{{ t('settings.readOnly') }}</Badge>
          </div>
          <p class="max-w-2xl text-sm text-muted-foreground">{{ t('settings.description') }}</p>
        </div>
        <Button variant="outline" :disabled="loading" @click="loadSettings">
          <RefreshCw :class="['size-4', loading && 'animate-spin']" aria-hidden="true" />
          {{ t('settings.refresh') }}
        </Button>
      </div>

      <Alert v-if="error" variant="destructive">
        <AlertTitle>{{ t('settings.loadError') }}</AlertTitle>
        <AlertDescription>{{ t('settings.securityNote') }}</AlertDescription>
      </Alert>

      <div v-if="loading && !settings" class="text-sm text-muted-foreground" role="status">{{ t('settings.loading') }}</div>

      <div v-if="settings" class="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>{{ t('settings.application') }}</CardTitle><CardDescription>{{ t('settings.environment') }}</CardDescription></CardHeader>
          <CardContent class="grid gap-4 sm:grid-cols-2">
            <div><p class="text-xs text-muted-foreground">{{ t('settings.appName') }}</p><p class="mt-1 font-medium">{{ settings.app_name }}</p></div>
            <div><p class="text-xs text-muted-foreground">{{ t('settings.environment') }}</p><p class="mt-1 font-medium">{{ settings.environment }}</p></div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>{{ t('settings.features') }}</CardTitle><CardDescription>{{ t('settings.apiDocs') }}</CardDescription></CardHeader>
          <CardContent class="flex items-center justify-between">
            <span class="text-sm">{{ t('settings.apiDocs') }}</span>
            <Badge :variant="settings.api_docs_enabled ? 'secondary' : 'outline'">{{ settings.api_docs_enabled ? t('settings.enabled') : t('settings.disabled') }}</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>{{ t('settings.connections') }}</CardTitle><CardDescription>{{ t('settings.connectionDescription') }}</CardDescription></CardHeader>
          <CardContent class="grid gap-3 sm:grid-cols-2">
            <div class="rounded-md border p-3"><div class="flex items-center justify-between"><span>{{ t('settings.database') }}</span><Badge :variant="settings.database_configured ? 'secondary' : 'outline'">{{ configured(settings.database_configured) }}</Badge></div><p v-if="health" class="mt-2 text-xs text-muted-foreground">{{ t('settings.liveStatus') }}: {{ statusLabel(health.database) }}</p></div>
            <div class="rounded-md border p-3"><div class="flex items-center justify-between"><span>{{ t('settings.redis') }}</span><Badge :variant="settings.redis_configured ? 'secondary' : 'outline'">{{ configured(settings.redis_configured) }}</Badge></div><p v-if="health" class="mt-2 text-xs text-muted-foreground">{{ t('settings.liveStatus') }}: {{ statusLabel(health.redis) }}</p></div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle>{{ t('settings.runtime') }}</CardTitle><CardDescription><ShieldCheck class="mr-1 inline size-4" aria-hidden="true" />{{ t('settings.readOnly') }}</CardDescription></CardHeader>
          <CardContent class="grid gap-3 sm:grid-cols-2">
            <div><p class="text-xs text-muted-foreground">{{ t('settings.tokenLifetime') }}</p><p class="mt-1 font-medium">{{ settings.jwt_access_token_minutes }} {{ t('settings.minutes') }}</p></div>
            <div><p class="text-xs text-muted-foreground">{{ t('settings.taskLease') }}</p><p class="mt-1 font-medium">{{ settings.task_lease_seconds }} {{ t('settings.seconds') }}</p></div>
          </CardContent>
        </Card>
      </div>
    </main>
  </AdminShell>
</template>
