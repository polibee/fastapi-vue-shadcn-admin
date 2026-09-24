<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>

<template>
  <main class="flex min-h-svh items-center justify-center bg-muted/30 p-6">
    <section class="grid max-w-md gap-3 text-center">
      <p class="text-6xl font-semibold text-muted-foreground">404</p>
      <h1 class="text-2xl font-semibold">{{ t('common.notFound.title') }}</h1>
      <p class="text-sm text-muted-foreground">{{ t('common.notFound.description') }}</p>
    </section>
  </main>
</template>
