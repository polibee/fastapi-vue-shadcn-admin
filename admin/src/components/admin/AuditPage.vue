<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronLeft, ChevronRight, ClipboardList, RefreshCw } from '@lucide/vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { fetchHealth, type HealthStatus } from '@/core/api/health'
import { fetchAuditLogs, type AuditLogItem } from '@/core/api/resources'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const items = ref<AuditLogItem[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref(false)
const search = ref('')
const offset = ref(0)
const pageSize = 10
const healthStatus = ref<HealthStatus>('unavailable')

async function loadAuditLogs() {
  loading.value = true
  error.value = false
  try {
    const result = await fetchAuditLogs({ offset: offset.value, limit: pageSize, search: search.value })
    items.value = result.items
    total.value = result.total
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

async function submitSearch() {
  offset.value = 0
  await loadAuditLogs()
}

async function changePage(nextOffset: number) {
  offset.value = nextOffset
  await loadAuditLogs()
}

onMounted(async () => {
  await Promise.allSettled([
    loadAuditLogs(),
    fetchHealth().then((health) => { healthStatus.value = health.status }),
  ])
})
</script>

<template>
  <AdminShell :system-status="healthStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end"><div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ t('nav.manage') }}</p><h1 class="text-3xl font-semibold tracking-tight">{{ t('audit.title') }}</h1><p class="text-sm text-muted-foreground">{{ t('audit.description') }}</p></div><Button variant="outline" :disabled="loading" @click="loadAuditLogs"><RefreshCw data-icon="inline-start" :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ t('audit.refresh') }}</Button></section>
      <Alert v-if="error" variant="destructive"><AlertTitle>{{ t('audit.loadFailed') }}</AlertTitle><AlertDescription>{{ t('audit.loadFailed') }}</AlertDescription></Alert>
      <Card><CardHeader><CardTitle class="flex items-center gap-2"><ClipboardList aria-hidden="true" />{{ t('audit.title') }}</CardTitle><CardDescription>{{ t('audit.total', { count: total }) }}</CardDescription></CardHeader><CardContent class="grid gap-4"><form class="flex flex-col gap-2 sm:flex-row" @submit.prevent="submitSearch"><Input v-model="search" :placeholder="t('audit.searchPlaceholder')" :aria-label="t('audit.searchPlaceholder')" /><Button type="submit" variant="outline">{{ t('audit.search') }}</Button></form><div v-if="!loading && items.length === 0" class="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">{{ t('audit.empty') }}</div><div v-for="item in items" :key="item.id" class="grid gap-2 rounded-md border p-4 text-sm md:grid-cols-[auto_1fr_1fr_2fr]"><div><p class="font-medium">{{ item.action }}</p><p class="text-muted-foreground">{{ item.resource }} #{{ item.resource_id ?? '—' }}</p></div><p><span class="text-muted-foreground">{{ t('audit.actor') }}:</span> {{ item.actor_user_id ?? '—' }}</p><p><span class="text-muted-foreground">{{ t('audit.requestId') }}:</span> <span class="break-all font-mono text-xs">{{ item.request_id }}</span></p><p class="text-muted-foreground">{{ new Date(item.created_at).toLocaleString() }}</p></div><div class="flex items-center justify-between border-t pt-4"><span class="text-sm text-muted-foreground">{{ t('audit.page', { current: Math.floor(offset / pageSize) + 1, total: Math.max(1, Math.ceil(total / pageSize)) }) }}</span><div class="flex gap-2"><Button variant="outline" size="sm" :disabled="loading || offset === 0" :aria-label="t('audit.previous')" @click="changePage(Math.max(0, offset - pageSize))"><ChevronLeft class="size-4" aria-hidden="true" />{{ t('audit.previous') }}</Button><Button variant="outline" size="sm" :disabled="loading || offset + pageSize >= total" :aria-label="t('audit.next')" @click="changePage(offset + pageSize)">{{ t('audit.next') }}<ChevronRight class="size-4" aria-hidden="true" /></Button></div></div></CardContent></Card>
    </main>
  </AdminShell>
</template>
