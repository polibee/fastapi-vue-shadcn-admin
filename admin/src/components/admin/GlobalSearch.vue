<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowRight, Search } from '@lucide/vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandShortcut } from '@/components/ui/command'
import type { ResourceManifest } from '@/core/resources/types'
import { buildSearchRegistry, type SearchEntry } from '@/core/search/registry'

const props = defineProps<{ manifests: ResourceManifest[] }>()
const { t } = useI18n()
const router = useRouter()
const open = ref(false)
const entries = computed(() => buildSearchRegistry(props.manifests))
const workspaceEntries = computed(() => entries.value.filter((entry) => entry.group === 'workspace'))
const manageEntries = computed(() => entries.value.filter((entry) => entry.group === 'manage'))

function handleShortcut(event: KeyboardEvent) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    open.value = !open.value
  }
}

function navigate(entry: SearchEntry) {
  open.value = false
  void router.push(entry.to)
}

onMounted(() => window.addEventListener('keydown', handleShortcut))
onUnmounted(() => window.removeEventListener('keydown', handleShortcut))
</script>

<template>
  <Button variant="outline" size="sm" class="hidden min-w-32 justify-between sm:flex" :aria-label="t('search.open')" @click="open = true">
    <span class="flex items-center gap-2"><Search data-icon="inline-start" aria-hidden="true" />{{ t('search.open') }}</span>
    <CommandShortcut>⌘K</CommandShortcut>
  </Button>
  <CommandDialog v-model:open="open" :title="t('search.title')" :description="t('search.description')">
    <CommandInput :placeholder="t('search.placeholder')" />
    <CommandList>
      <CommandEmpty>{{ t('search.noResults') }}</CommandEmpty>
      <CommandGroup :heading="t('search.workspace')">
        <CommandItem v-for="entry in workspaceEntries" :key="entry.id" :value="t(entry.labelKey)" @select="navigate(entry)">
          <ArrowRight aria-hidden="true" />
          <span>{{ t(entry.labelKey) }}</span>
          <CommandShortcut>↵</CommandShortcut>
        </CommandItem>
      </CommandGroup>
      <CommandGroup :heading="t('search.manage')">
        <CommandItem v-for="entry in manageEntries" :key="entry.id" :value="t(entry.labelKey)" @select="navigate(entry)">
          <ArrowRight aria-hidden="true" />
          <span>{{ t(entry.labelKey) }}</span>
          <CommandShortcut>↵</CommandShortcut>
        </CommandItem>
      </CommandGroup>
    </CommandList>
  </CommandDialog>
</template>
