<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ClipboardList, Plus, RefreshCw } from '@lucide/vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { cancelTask, createTask, fetchTaskEvents, fetchTasks, retryTask, type TaskEvent, type TaskItem } from '@/core/api/resources'
import { currentUser } from '@/core/permissions'
import { canManageTask } from '@/core/tasks'
import AdminShell from './AdminShell.vue'

const { t } = useI18n()
const tasks = ref<TaskItem[]>([])
const events = ref<Record<string, TaskEvent[]>>({})
const total = ref(0)
const loading = ref(false)
const error = ref(false)
const formOpen = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const taskName = ref('demo.sync')
const payload = ref('{"dry_run":true}')

async function loadTasks() {
  loading.value = true
  error.value = false
  try {
    const result = await fetchTasks()
    tasks.value = result.items
    total.value = result.total
    const entries = await Promise.all(result.items.map(async (task) => [task.task_id, await fetchTaskEvents(task.task_id)] as const))
    events.value = Object.fromEntries(entries)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

async function submitTask() {
  formError.value = !taskName.value.trim() ? 'taskNameRequired' : null
  if (formError.value) return
  let parsedPayload: Record<string, unknown>
  try { parsedPayload = JSON.parse(payload.value) as Record<string, unknown> } catch { formError.value = 'payloadInvalid'; return }
  submitting.value = true
  try {
    await createTask(taskName.value.trim(), parsedPayload)
    formOpen.value = false
    await loadTasks()
  } catch { formError.value = 'createFailed' } finally { submitting.value = false }
}

async function cancelPendingTask(task: TaskItem) {
  try { await cancelTask(task.task_id); await loadTasks() } catch { error.value = true }
}

async function retryFailedTask(task: TaskItem) {
  try { await retryTask(task.task_id); await loadTasks() } catch { error.value = true }
}

onMounted(loadTasks)
</script>

<template>
  <AdminShell>
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <section class="flex flex-col justify-between gap-4 md:flex-row md:items-end"><div class="grid gap-2"><p class="text-sm text-muted-foreground">{{ t('nav.workspace') }}</p><h1 class="text-3xl font-semibold tracking-tight">{{ t('tasks.title') }}</h1><p class="text-sm text-muted-foreground">{{ t('tasks.description') }}</p></div><div class="flex gap-2"><Button variant="outline" :disabled="loading" @click="loadTasks"><RefreshCw data-icon="inline-start" :class="loading ? 'animate-spin' : ''" aria-hidden="true" />{{ t('tasks.refresh') }}</Button><Button v-if="!formOpen && currentUser?.permissions.includes('tasks.create')" @click="formOpen = true"><Plus data-icon="inline-start" aria-hidden="true" />{{ t('tasks.create') }}</Button></div></section>
      <Card v-if="formOpen"><CardHeader><CardTitle>{{ t('tasks.create') }}</CardTitle><CardDescription>{{ t('tasks.createDescription') }}</CardDescription></CardHeader><CardContent><form class="grid gap-4 md:grid-cols-2" @submit.prevent="submitTask"><Input v-model="taskName" :placeholder="t('tasks.taskName')" /><Input v-model="payload" :placeholder="t('tasks.payload')" class="md:col-span-2" /><div class="flex gap-2 md:col-span-2"><Button type="submit" :disabled="submitting">{{ submitting ? t('tasks.creating') : t('tasks.save') }}</Button><Button type="button" variant="outline" @click="formOpen = false">{{ t('tasks.cancel') }}</Button></div><p v-if="formError" class="text-sm text-destructive md:col-span-2">{{ t(`tasks.${formError}`) }}</p></form></CardContent></Card>
      <Alert v-if="error" variant="destructive"><AlertTitle>{{ t('tasks.loadFailed') }}</AlertTitle><AlertDescription>{{ t('tasks.loadFailed') }}</AlertDescription></Alert>
      <Card><CardHeader><CardTitle class="flex items-center gap-2"><ClipboardList aria-hidden="true" />{{ t('tasks.title') }}</CardTitle><CardDescription>{{ t('tasks.total', { count: total }) }}</CardDescription></CardHeader><CardContent class="grid gap-3"><div v-if="!loading && tasks.length === 0" class="rounded-md border border-dashed p-8 text-center text-sm text-muted-foreground">{{ t('tasks.empty') }}</div><div v-for="task in tasks" :key="task.task_id" class="grid gap-3 rounded-md border p-4"><div class="flex flex-col justify-between gap-3 md:flex-row"><div><p class="font-medium">{{ task.task_name }}</p><p class="break-all font-mono text-xs text-muted-foreground">{{ task.task_id }}</p><p class="text-xs text-muted-foreground">{{ task.request_id }}</p><p class="text-xs text-muted-foreground">{{ task.progress }}% · {{ task.message || '—' }}</p><p v-if="task.error_message" class="text-xs text-destructive">{{ task.error_message }}</p></div><div class="flex items-start gap-2"><Badge variant="outline">{{ task.status }}</Badge><Button v-if="canManageTask(task.status, 'tasks.cancel', currentUser?.permissions ?? [])" variant="outline" size="sm" @click="cancelPendingTask(task)">{{ t('tasks.cancelTask') }}</Button><Button v-if="canManageTask(task.status, 'tasks.retry', currentUser?.permissions ?? [])" variant="outline" size="sm" @click="retryFailedTask(task)">{{ t('tasks.retryTask') }}</Button></div></div><div v-if="events[task.task_id]?.length" class="border-t pt-3"><p class="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">{{ t('tasks.timeline') }}</p><ol class="grid gap-2 border-l pl-4"><li v-for="event in events[task.task_id]" :key="event.id" class="relative text-xs"><span class="absolute -left-[1.35rem] top-1 size-2 rounded-full bg-primary" aria-hidden="true"></span><div class="flex flex-wrap gap-x-2"><span class="font-medium">{{ t(`tasks.events.${event.event_type}`, event.event_type) }}</span><span class="text-muted-foreground">{{ new Date(event.created_at).toLocaleString() }}</span></div><p class="text-muted-foreground">{{ event.message }}</p></li></ol></div></div></CardContent></Card>
    </main>
  </AdminShell>
</template>
