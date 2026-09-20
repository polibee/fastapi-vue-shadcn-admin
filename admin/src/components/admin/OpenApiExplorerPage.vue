<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { BookOpen, RefreshCw } from '@lucide/vue'
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { fetchOpenApiDocument, listOpenApiOperations, type OpenApiDocument, type OpenApiOperation } from '@/core/api/openapi'
import { fetchHealth, type HealthStatus } from '@/core/api/health'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const document = ref<OpenApiDocument | null>(null)
const operations = ref<OpenApiOperation[]>([])
const selectedTag = ref('')
const loading = ref(false)
const error = ref(false)
const healthStatus = ref<HealthStatus>('unavailable')
const tags = computed(() => [...new Set(operations.value.flatMap((operation) => operation.tags))].sort())
const filteredOperations = computed(() => selectedTag.value ? operations.value.filter((operation) => operation.tags.includes(selectedTag.value)) : operations.value)

async function loadOpenApi() {
  loading.value = true
  error.value = false
  try {
    const [nextDocument, health] = await Promise.all([fetchOpenApiDocument(), fetchHealth()])
    document.value = nextDocument
    operations.value = listOpenApiOperations(nextDocument)
    healthStatus.value = health.status
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(loadOpenApi)
</script>

<template>
  <AdminShell :system-status="healthStatus">
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end"><div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ t('nav.manage') }}</p><h1 class="flex items-center gap-2 text-3xl font-semibold tracking-tight"><BookOpen class="size-6" aria-hidden="true" />{{ t('openapi.title') }}</h1><p class="text-sm text-muted-foreground">{{ t('openapi.description') }}</p></div><Button variant="outline" :disabled="loading" @click="loadOpenApi"><RefreshCw :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ t('openapi.refresh') }}</Button></section>
      <p v-if="error" class="rounded-md border border-destructive/50 p-4 text-sm text-destructive" role="alert">{{ t('openapi.loadError') }}</p>
      <p v-if="loading && !document" class="text-sm text-muted-foreground" role="status">{{ t('openapi.loading') }}</p>
      <template v-if="document"><div class="grid gap-4 sm:grid-cols-2"><Card><CardHeader class="pb-2"><CardDescription>{{ t('openapi.version') }}</CardDescription><CardTitle class="text-xl">{{ document.openapi }}</CardTitle></CardHeader></Card><Card><CardHeader class="pb-2"><CardDescription>{{ t('openapi.operations') }}</CardDescription><CardTitle class="text-xl">{{ operations.length }}</CardTitle></CardHeader></Card></div><div class="flex flex-wrap gap-2" role="group" :aria-label="t('openapi.filter')"><Button size="sm" :variant="selectedTag === '' ? 'default' : 'outline'" @click="selectedTag = ''">{{ t('openapi.all') }}</Button><Button v-for="tag in tags" :key="tag" size="sm" :variant="selectedTag === tag ? 'default' : 'outline'" @click="selectedTag = tag">{{ tag }}</Button></div><Card><CardContent class="p-0"><div v-if="filteredOperations.length" class="divide-y"><div v-for="operation in filteredOperations" :key="`${operation.method}:${operation.path}`" class="grid gap-2 px-4 py-3 text-sm md:grid-cols-[100px_2fr_2fr] md:items-center"><div><Badge variant="outline">{{ operation.method }}</Badge></div><div class="break-all font-mono">{{ operation.path }}</div><div class="text-muted-foreground">{{ operation.summary || '—' }}</div></div></div><p v-else class="p-8 text-center text-sm text-muted-foreground">{{ t('openapi.empty') }}</p></CardContent></Card></template>
    </main>
  </AdminShell>
</template>
