<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Database, KeyRound, RefreshCw } from '@lucide/vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { fetchDatabaseIntrospection, fetchResourceCompatibility, type DatabaseIntrospection, type ResourceCompatibility } from '@/core/api/introspection'
import { fetchHealth, type HealthStatus } from '@/core/api/health'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const result = ref<DatabaseIntrospection | null>(null)
const compatibility = ref<ResourceCompatibility[]>([])
const loading = ref(false)
const error = ref(false)
const healthStatus = ref<HealthStatus>('unavailable')
const tableCount = computed(() => result.value?.tables.length ?? 0)

async function loadIntrospection() {
  loading.value = true
  error.value = false
  try {
    const [introspection, health, compatibilityResult] = await Promise.all([fetchDatabaseIntrospection(), fetchHealth(), fetchResourceCompatibility()])
    result.value = introspection
    healthStatus.value = health.status
    compatibility.value = compatibilityResult
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadIntrospection)
</script>

<template>
  <AdminShell :system-status="healthStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ t('nav.manage') }}</p><h1 class="text-3xl font-semibold tracking-tight">{{ t('introspection.title') }}</h1><p class="text-sm text-muted-foreground">{{ t('introspection.description') }}</p></div>
        <Button variant="outline" :disabled="loading" @click="loadIntrospection"><RefreshCw :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ t('introspection.refresh') }}</Button>
      </section>
      <p v-if="error" class="rounded-md border border-destructive/50 p-4 text-sm text-destructive" role="alert">{{ t('introspection.loadError') }}</p>
      <p v-if="loading && !result" class="text-sm text-muted-foreground" role="status">{{ t('introspection.loading') }}</p>
      <template v-if="result">
        <div class="grid gap-4 sm:grid-cols-4"><Card><CardHeader class="pb-2"><CardDescription>{{ t('introspection.dialect') }}</CardDescription><CardTitle class="text-xl">{{ result.dialect }}</CardTitle></CardHeader></Card><Card><CardHeader class="pb-2"><CardDescription>{{ t('introspection.schema') }}</CardDescription><CardTitle class="text-xl">{{ result.schema || '—' }}</CardTitle></CardHeader></Card><Card><CardHeader class="pb-2"><CardDescription>{{ t('introspection.tables') }}</CardDescription><CardTitle class="text-xl">{{ tableCount }}</CardTitle></CardHeader></Card><Card><CardHeader class="pb-2"><CardDescription>{{ t('introspection.views') }}</CardDescription><CardTitle class="text-xl">{{ result.views.length }}</CardTitle></CardHeader></Card></div>
        <div v-if="result.tables.length" class="grid gap-4 lg:grid-cols-2">
          <Card v-for="table in result.tables" :key="table.name"><CardHeader><CardTitle class="flex items-center gap-2"><Database class="size-4" aria-hidden="true" />{{ table.name }}</CardTitle><CardDescription>{{ table.columns.length }} {{ t('introspection.columns') }} · {{ table.indexes.length }} {{ t('introspection.indexes') }} · {{ table.foreignKeys.length }} {{ t('introspection.foreignKeys') }}</CardDescription></CardHeader><CardContent class="grid gap-2"><div v-for="column in table.columns" :key="column.name" class="flex items-center justify-between rounded-md border px-3 py-2 text-sm"><span class="font-mono">{{ column.name }}</span><span class="flex items-center gap-2 text-muted-foreground"><KeyRound v-if="column.primaryKey" class="size-3" :aria-label="t('introspection.primaryKey')" /><Badge variant="outline">{{ column.type }}</Badge><span v-if="!column.nullable">!</span></span></div><div v-if="table.indexes.length" class="border-t pt-3 text-xs text-muted-foreground">{{ table.indexes.map((index) => `${index.name}${index.unique ? ` (${t('introspection.unique')})` : ''}`).join(' · ') }}</div><div v-if="table.foreignKeys.length" class="text-xs text-muted-foreground">{{ table.foreignKeys.map((foreignKey) => `${foreignKey.columns.join(', ')} → ${foreignKey.referredTable}`).join(' · ') }}</div></CardContent></Card>
        </div>
        <p v-else class="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">{{ t('introspection.empty') }}</p>
        <Card><CardHeader><CardTitle>{{ t('introspection.compatibility') }}</CardTitle></CardHeader><CardContent class="grid gap-2"><div v-for="item in compatibility" :key="item.resource" class="flex flex-col gap-2 rounded-md border p-3 text-sm sm:flex-row sm:items-center sm:justify-between"><span class="font-medium">{{ item.resource }}</span><div class="flex flex-wrap items-center gap-2"><Badge :variant="item.status === 'ok' ? 'secondary' : 'destructive'">{{ item.status === 'ok' ? t('introspection.compatible') : item.status === 'drift' ? t('introspection.drift') : t('introspection.missingTable') }}</Badge><span v-if="item.missingColumns.length" class="text-xs text-muted-foreground">{{ t('introspection.missingColumns') }}: {{ item.missingColumns.join(', ') }}</span><span v-if="item.extraColumns.length" class="text-xs text-muted-foreground">{{ t('introspection.extraColumns') }}: {{ item.extraColumns.join(', ') }}</span></div></div></CardContent></Card>
      </template>
    </main>
  </AdminShell>
</template>
