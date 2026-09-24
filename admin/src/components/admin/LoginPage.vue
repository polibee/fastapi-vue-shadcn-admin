<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Check, Copy, Globe2, LogIn } from '@lucide/vue'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ApiError, demoCredentials, login } from '@/core/api/auth'
import { setLocale } from '@/locales'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { adminPath, safeAdminRedirect } from '@/router/paths'

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const errorCode = ref('')
const copiedField = ref<'username' | 'password' | null>(null)
const isDevelopment = import.meta.env.DEV && import.meta.env.VITE_DEMO_LOGIN_ENABLED !== 'false'

async function changeLocale(nextLocale: 'zh-CN' | 'en') {
  await setLocale(nextLocale, ['common', 'shell', 'auth', 'users', 'roles'])
  window.localStorage.setItem('admin-locale', nextLocale)
}

async function copyCredential(field: 'username' | 'password') {
  await navigator.clipboard.writeText(demoCredentials[field])
  copiedField.value = field
  window.setTimeout(() => { copiedField.value = null }, 1600)
}

function fillDemoCredentials() {
  username.value = demoCredentials.username
  password.value = demoCredentials.password
}

async function signInWithDemo() {
  fillDemoCredentials()
  await submit()
}

async function submit() {
  errorMessage.value = ''
  errorCode.value = ''
  loading.value = true
  try {
    await login({ username: username.value, password: password.value })
    await router.replace(safeAdminRedirect(typeof route.query.redirect === 'string' ? route.query.redirect : adminPath('/')))
  } catch (error) {
    if (error instanceof ApiError) {
      errorCode.value = error.code
      errorMessage.value = error.message
    } else {
      errorMessage.value = error instanceof Error ? error.message : t('auth.loginFailed')
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="flex min-h-svh items-center justify-center bg-muted/30 p-4">
    <Card class="w-full max-w-md">
      <CardHeader class="gap-4">
        <div class="flex items-start justify-between gap-4">
          <div class="grid gap-1">
            <CardTitle>{{ t('auth.title') }}</CardTitle>
            <CardDescription>{{ t('auth.description') }}</CardDescription>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="outline" size="sm" :aria-label="t('common.languageSwitcher')">
                <Globe2 data-icon="inline-start" aria-hidden="true" />
                <span class="hidden sm:inline">{{ locale === 'zh-CN' ? t('common.languageZh') : t('common.languageEn') }}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-44">
              <DropdownMenuLabel>{{ t('common.languageSwitcher') }}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem @select="changeLocale('zh-CN')">
                <Check v-if="locale === 'zh-CN'" aria-hidden="true" /><span v-else class="size-4" aria-hidden="true" />{{ t('common.languageZh') }}
              </DropdownMenuItem>
              <DropdownMenuItem @select="changeLocale('en')">
                <Check v-if="locale === 'en'" aria-hidden="true" /><span v-else class="size-4" aria-hidden="true" />{{ t('common.languageEn') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <form @submit.prevent="submit">
        <CardContent class="grid gap-5">
          <Alert v-if="errorMessage" variant="destructive" role="alert">
            <AlertTitle>{{ t('auth.loginFailed') }}</AlertTitle>
            <AlertDescription>{{ errorCode ? t(`auth.errors.${errorCode}`) : errorMessage }}</AlertDescription>
          </Alert>
          <div class="grid gap-2">
            <label for="username" class="text-sm font-medium">{{ t('auth.username') }}</label>
            <Input id="username" v-model="username" autocomplete="username" required :placeholder="t('auth.usernamePlaceholder')" />
          </div>
          <div class="grid gap-2">
            <label for="password" class="text-sm font-medium">{{ t('auth.password') }}</label>
            <Input id="password" v-model="password" autocomplete="current-password" required type="password" :placeholder="t('auth.passwordPlaceholder')" />
          </div>
          <div v-if="isDevelopment" class="grid gap-2 rounded-md border border-dashed p-3">
            <p class="text-xs font-medium text-muted-foreground">{{ t('auth.demoTitle') }}</p>
            <div class="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
              <code>{{ demoCredentials.username }}</code>
              <Button type="button" variant="ghost" size="sm" @click="copyCredential('username')">
                <Check v-if="copiedField === 'username'" data-icon="inline-start" aria-hidden="true" /><Copy v-else data-icon="inline-start" aria-hidden="true" />
                {{ copiedField === 'username' ? t('auth.copied') : t('auth.copyUsername') }}
              </Button>
              <code>{{ demoCredentials.password }}</code>
              <Button type="button" variant="ghost" size="sm" @click="copyCredential('password')">
                <Check v-if="copiedField === 'password'" data-icon="inline-start" aria-hidden="true" /><Copy v-else data-icon="inline-start" aria-hidden="true" />
                {{ copiedField === 'password' ? t('auth.copied') : t('auth.copyPassword') }}
              </Button>
            </div>
            <Button type="button" variant="secondary" class="w-full" @click="signInWithDemo">{{ t('auth.demoSignIn') }}</Button>
          </div>
        </CardContent>
        <CardFooter class="pt-1">
          <Button class="w-full" type="submit" :disabled="loading">
            <LogIn data-icon="inline-start" aria-hidden="true" />
            {{ loading ? t('auth.signingIn') : t('auth.signIn') }}
          </Button>
        </CardFooter>
      </form>
    </Card>
  </main>
</template>
