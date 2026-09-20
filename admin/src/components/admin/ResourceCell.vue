<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Badge } from '@/components/ui/badge'
import type { ResourceField } from '@/core/resources/types'
import { formatResourceValue } from '@/core/resources/formatters'

const props = defineProps<{
  field: ResourceField
  value: unknown
  namespace: string
}>()

const { t } = useI18n()
</script>

<template>
  <Badge v-if="field.type === 'boolean'" :variant="value ? 'secondary' : 'outline'">
    {{ value ? t(`${namespace}.active`) : t(`${namespace}.inactive`) }}
  </Badge>
  <span v-else>{{ formatResourceValue(field, value) }}</span>
</template>
