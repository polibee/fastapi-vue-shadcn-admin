<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { Activity, Database, ListTodo, RefreshCw, Server, Users } from '@lucide/vue'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { dashboardWidgetRegistry } from '@/core/dashboard-registry'
import { fetchHealth, type HealthStatus, type HealthSummary } from '@/core/api/health'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const loading = ref(true)
const lastSyncedAt = ref<Date | null>(null)
const syncFailed = ref(false)
let refreshTimer: number | undefined
const health = ref<HealthSummary>({ status: 'unavailable', database: 'unavailable', redis: 'unavailable', tasks: { total: 0, pending: 0, running: 0, failed: 0, dead: 0 } })

const serviceIcons: Record<string, typeof Server> = { api: Server, worker: ListTodo, database: Database, redis: Activity }
const statIcons: Record<string, typeof Users> = { users: Users, tasks: ListTodo, api: Server, activity: Activity }
function statusLabel(status: HealthStatus) {
  if (status === 'ok') return t('health.operational')
  if (status === 'degraded') return t('health.degraded')
  return t('health.unavailable')
}

function serviceStatus(source: string): HealthStatus {
  if (source === 'database') return health.value.database
  if (source === 'redis') return health.value.redis
  return health.value.status
}

function syncedLabel() {
  return lastSyncedAt.value ? new Intl.DateTimeFormat(undefined, { hour: '2-digit', minute: '2-digit', second: '2-digit' }).format(lastSyncedAt.value) : ''
}

async function refreshHealth() {
  loading.value = true
  try {
    health.value = await fetchHealth()
    lastSyncedAt.value = new Date()
    syncFailed.value = false
  } catch {
    health.value = { status: 'unavailable', database: 'unavailable', redis: 'unavailable', tasks: { total: 0, pending: 0, running: 0, failed: 0, dead: 0 } }
    syncFailed.value = true
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await refreshHealth()
  refreshTimer = window.setInterval(() => void refreshHealth, 30000)
})

onUnmounted(() => {
  if (refreshTimer) window.clearInterval(refreshTimer)
})
</script>

<template>
  <AdminShell :system-status="health.status">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div class="grid gap-2">
          <p class="text-sm text-muted-foreground">{{ t('dashboard.eyebrow') }}</p>
          <h1 class="text-3xl font-semibold tracking-tight">{{ t('dashboard.greeting') }}</h1>
          <p class="max-w-xl text-sm text-muted-foreground">{{ t('dashboard.description') }}</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <div class="inline-flex items-center gap-2 rounded-full border border-border bg-muted/40 px-3 py-1.5 text-xs text-muted-foreground" role="status" :aria-label="loading ? t('dashboard.syncing') : syncFailed ? t('dashboard.syncFailed') : t('dashboard.lastSynced', { time: syncedLabel() })">
            <span class="relative flex size-2" aria-hidden="true">
              <span v-if="loading" class="absolute inline-flex size-full animate-ping rounded-full bg-primary/60" />
              <span class="relative inline-flex size-2 rounded-full" :class="syncFailed ? 'bg-destructive' : loading ? 'bg-primary' : 'bg-primary/80'" />
            </span>
            <span v-if="loading">{{ t('dashboard.syncing') }}</span>
            <span v-else-if="syncFailed">{{ t('dashboard.syncFailed') }}</span>
            <span v-else>{{ t('dashboard.lastSynced', { time: syncedLabel() }) }}</span>
          </div>
          <a href="https://github.com/polibee/fastapi-vue-shadcn-admin" target="_blank" rel="noreferrer" class="text-xs text-primary underline-offset-4 hover:underline">{{ t('dashboard.repository') }}</a>
          <Button variant="outline" @click="refreshHealth()">
            <RefreshCw data-icon="inline-start" :class="loading ? 'animate-spin' : ''" aria-hidden="true" />
            {{ t('dashboard.refresh') }}
          </Button>
        </div>
      </section>

      <Alert v-if="health.status === 'unavailable'" variant="destructive">
        <AlertTitle>{{ t('health.unavailable') }}</AlertTitle>
        <AlertDescription>{{ t('dashboard.description') }}</AlertDescription>
      </Alert>

      <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" :aria-label="t('dashboard.stats.activeUsers')">
        <Card v-for="stat in dashboardWidgetRegistry.stats" :key="stat.id">
          <CardHeader class="flex-row items-center justify-between space-y-0 pb-2">
            <CardDescription>{{ t(stat.labelKey) }}</CardDescription>
            <component :is="statIcons[stat.icon]" class="size-4 text-muted-foreground" aria-hidden="true" />
          </CardHeader>
          <CardContent>
            <CardTitle class="text-2xl">{{ stat.valueSource === 'health.tasks.pending' ? health.tasks.pending : t('common.notAvailable') }}</CardTitle>
            <p class="mt-1 text-xs text-muted-foreground">{{ stat.changeKey === 'needsReview' ? t('dashboard.stats.needsReview') : t('common.notAvailable') }} · {{ t(`dashboard.stats.${stat.detailKey}`) }}</p>
          </CardContent>
        </Card>
      </section>

      <section class="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>{{ t('dashboard.health.title') }}</CardTitle><CardDescription>{{ t('dashboard.description') }}</CardDescription></CardHeader>
          <CardContent class="grid gap-4">
            <div v-for="service in dashboardWidgetRegistry.services" :key="service.id" class="grid gap-2">
              <div class="flex items-center justify-between text-sm"><span class="flex items-center gap-2"><component :is="serviceIcons[service.icon]" class="size-4 text-muted-foreground" aria-hidden="true" />{{ t(service.labelKey) }}</span><Badge :variant="serviceStatus(service.healthSource) === 'ok' ? 'secondary' : 'outline'">{{ statusLabel(serviceStatus(service.healthSource)) }}</Badge></div>
              <Progress :model-value="serviceStatus(service.healthSource) === 'ok' ? 100 : 0" :aria-label="t(service.labelKey)" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader><CardTitle>{{ t('dashboard.activity.title') }}</CardTitle><CardDescription>{{ t('dashboard.description') }}</CardDescription></CardHeader>
          <CardContent><div class="flex min-h-32 items-center justify-center rounded-md border border-dashed p-6 text-center text-sm text-muted-foreground">{{ t('dashboard.description') }}</div></CardContent>
        </Card>
      </section>

      <Card>
        <CardHeader><CardTitle>{{ t('dashboard.milestone.title') }}</CardTitle><CardDescription>{{ t('dashboard.milestone.description') }}</CardDescription></CardHeader>
        <CardContent class="grid gap-3"><div class="flex items-center justify-between text-sm"><span>{{ t('dashboard.milestone.title') }}</span><span class="text-muted-foreground">{{ t('dashboard.milestone.complete') }}</span></div><Progress :model-value="0" :aria-label="t('dashboard.milestone.title')" /></CardContent>
      </Card>
    </main>

  </AdminShell>
</template>
