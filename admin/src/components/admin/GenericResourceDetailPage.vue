<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { loadResourceManifest, resourceAdapterRegistry, validateResourceForm } from '@/core/resources'
import type { ResourceManifest } from '@/core/resources/types'
import ResourceDetailPageShell from './ResourceDetailPageShell.vue'
import ResourceForm from './ResourceForm.vue'
import { adminPath } from '@/router/paths'

const props = defineProps<{ resourceName: string; namespace: string }>()
const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const manifest = ref<ResourceManifest | null>(null)
const record = ref<Record<string, unknown> | null>(null)
const form = ref<Record<string, string>>({})
const loading = ref(true)
const saving = ref(false)
const error = ref(false)
const formError = ref<string | null>(null)

async function loadDetails() {
  loading.value = true; error.value = false
  try {
    manifest.value = await loadResourceManifest(props.resourceName)
    const adapter = resourceAdapterRegistry.get<any, any>(props.resourceName)
    if (!adapter.get) throw new Error('resource_detail_not_supported')
    record.value = await adapter.get(Number(route.params.id))
    form.value = Object.fromEntries(Object.entries(record.value as Record<string, unknown>).filter(([key]) => manifest.value?.forms.edit.fields.includes(key)).map(([key, value]) => [key, value == null ? '' : String(value)]))
  } catch { error.value = true } finally { loading.value = false }
}

async function save() {
  if (!manifest.value || !record.value) return
  formError.value = validateResourceForm(manifest.value, form.value)
  if (formError.value) return
  saving.value = true; error.value = false
  try {
    const adapter = resourceAdapterRegistry.get<any, any>(props.resourceName)
    if (!adapter.update) throw new Error('resource_update_not_supported')
    record.value = await adapter.update(Number(route.params.id), { ...form.value, id: record.value.id, is_active: record.value.is_active } as any)
  } catch { error.value = true } finally { saving.value = false }
}

onMounted(loadDetails)
</script>

<template>
  <ResourceDetailPageShell :eyebrow="t('nav.manage')" :title="record?.name ? String(record.name) : t(`${namespace}.title`)" :description="t(`${namespace}.description`)" :back-label="t('common.back')" :back-to="adminPath(`/${resourceName}`)" :refresh-label="t(`${namespace}.refresh`)" :loading="loading" :error="error" :error-title="t(`${namespace}.loadFailed`)" :error-description="t(`${namespace}.loadFailed`)" @refresh="loadDetails">
    <Card v-if="manifest && record"><CardHeader><CardTitle>{{ t(`${namespace}.detailsTitle`) }}</CardTitle><CardDescription>{{ t(`${namespace}.detailsDescription`) }}</CardDescription></CardHeader><CardContent><ResourceForm v-model="form" :manifest="manifest" :submitting="saving" :error-key="formError" :translation-namespace="namespace" :submit-label="t(saving ? `${namespace}.saving` : `${namespace}.save`)" :cancel-label="t('common.cancel')" @submit="save" @cancel="router.push(adminPath(`/${resourceName}`))" /></CardContent></Card><div v-else-if="loading" class="rounded-xl border border-dashed p-12 text-center text-sm text-muted-foreground">{{ t('common.loading') }}</div><Button v-else variant="outline" @click="router.push(adminPath(`/${resourceName}`))">{{ t('common.back') }}</Button>
  </ResourceDetailPageShell>
</template>
