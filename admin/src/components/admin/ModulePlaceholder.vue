<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import AdminShell from './AdminShell.vue'

defineProps<{ titleKey: string }>()
const { t } = useI18n()
</script>

<template>
  <AdminShell>
    <main class="flex flex-1 flex-col gap-6 p-4 md:p-8">
      <Card>
        <CardHeader><CardTitle>{{ t(titleKey) }}</CardTitle><CardDescription>{{ t('placeholder.description') }}</CardDescription></CardHeader>
        <CardContent><Alert><AlertTitle>{{ t('placeholder.title') }}</AlertTitle><AlertDescription>{{ t('placeholder.description') }}</AlertDescription></Alert></CardContent>
      </Card>
    </main>
  </AdminShell>
</template>
