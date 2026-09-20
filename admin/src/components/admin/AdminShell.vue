<script setup lang="ts">
import { computed, onMounted, ref, type Component } from 'vue'
import { RouterLink } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Activity, BookOpen, Check, ChevronDown, ClipboardList, Database, Globe2, KeyRound, LayoutDashboard, ListTodo, Package, Settings, ShieldCheck, Sparkles, Users } from '@lucide/vue'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { Separator } from '@/components/ui/separator'
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarInset, SidebarMenu, SidebarMenuBadge, SidebarMenuButton, SidebarMenuItem, SidebarProvider, SidebarRail, SidebarTrigger } from '@/components/ui/sidebar'
import type { HealthStatus } from '@/core/api/health'
import { revokeRefreshToken } from '@/core/api/auth'
import { setLocale } from '@/locales'
import { useRouter } from 'vue-router'
import { clearCurrentUser, hasPermission } from '@/core/permissions'
import { loadResourceIndex } from '@/core/resources'
import type { ResourceManifest } from '@/core/resources/types'
import { buildNavigationRegistry, type NavigationIcon } from '@/core/navigation/registry'
import GlobalSearch from './GlobalSearch.vue'

const props = withDefaults(defineProps<{ systemStatus?: HealthStatus }>(), { systemStatus: 'unavailable' })

const { t, locale } = useI18n()
const router = useRouter()
const resourceManifests = ref<ResourceManifest[]>([])

type NavigationItem = {
  to: string
  label: string
  icon: Component
  permission?: string
  badge?: string
}

const navigationIcons: Record<NavigationIcon, Component> = {
  activity: Activity,
  dashboard: LayoutDashboard,
  tasks: ListTodo,
  users: Users,
  roles: ShieldCheck,
  audit: ClipboardList,
  settings: Settings,
  database: Database,
  generator: Sparkles,
  modules: Package,
  api: BookOpen,
  permissions: KeyRound,
}

async function changeLocale(nextLocale: 'zh-CN' | 'en') {
  await setLocale(nextLocale, ['common', 'shell', 'dashboard', 'placeholder', 'users', 'roles', 'audit', 'tasks', 'settings', 'introspection', 'generator', 'modules', 'openapi', 'permissions'])
  window.localStorage.setItem('admin-locale', nextLocale)
}

async function signOut() {
  try {
    await revokeRefreshToken()
  } finally {
    clearCurrentUser()
    router.replace('/login')
  }
}

onMounted(async () => {
  try {
    resourceManifests.value = await loadResourceIndex()
  } catch {
    resourceManifests.value = []
  }
})

const navigation = computed<{ workspace: NavigationItem[]; manage: NavigationItem[] }>(() => {
  const registry = buildNavigationRegistry(resourceManifests.value)
  const toNavigationItem = (item: typeof registry.workspace[number]): NavigationItem => ({
    to: item.to,
    label: t(item.labelKey),
    icon: navigationIcons[item.icon],
    permission: item.permission,
  })
  const workspace = registry.workspace.map(toNavigationItem)
  const manage = registry.manage.map(toNavigationItem)
  return {
    workspace: workspace.filter((item) => !item.permission || hasPermission(item.permission)),
    manage: manage.filter((item) => !item.permission || hasPermission(item.permission)),
  }
})
</script>

<template>
  <SidebarProvider>
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div class="flex items-center gap-2 px-2 py-2">
          <div class="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground">
            <LayoutDashboard class="size-4" aria-hidden="true" />
          </div>
          <div class="grid flex-1 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden">
            <span class="truncate font-semibold">{{ t('brand.name') }}</span>
            <span class="truncate text-xs text-muted-foreground">{{ t('brand.caption') }}</span>
          </div>
        </div>
        <Button variant="outline" class="mx-2 justify-between group-data-[collapsible=icon]:hidden">
          <span class="truncate">{{ t('workspace.name') }}</span>
          <ChevronDown class="size-4" aria-hidden="true" />
        </Button>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>{{ t('nav.workspace') }}</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem v-for="item in navigation.workspace" :key="item.to">
                <SidebarMenuButton as-child :tooltip="item.label">
                  <RouterLink :to="item.to"><component :is="item.icon" aria-hidden="true" /><span>{{ item.label }}</span></RouterLink>
                </SidebarMenuButton>
                <SidebarMenuBadge v-if="item.badge">{{ t(item.badge) }}</SidebarMenuBadge>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>{{ t('nav.manage') }}</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem v-for="item in navigation.manage" :key="item.to">
                <SidebarMenuButton as-child :tooltip="item.label">
                  <RouterLink :to="item.to"><component :is="item.icon" aria-hidden="true" /><span>{{ item.label }}</span></RouterLink>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton as-child :tooltip="t('nav.docs')">
              <a href="/docs/scalar" target="_blank" rel="noreferrer"><BookOpen aria-hidden="true" /><span>{{ t('nav.docs') }}</span></a>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <SidebarMenuButton :tooltip="t('common.administrator')">
                  <Avatar class="size-6"><AvatarFallback>A</AvatarFallback></Avatar>
                  <span>{{ t('common.admin') }}</span>
                  <ChevronDown class="ml-auto size-4" aria-hidden="true" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" side="top" class="w-56">
                <DropdownMenuLabel>{{ t('common.admin') }}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem>{{ t('nav.settings') }}</DropdownMenuItem>
                <DropdownMenuItem @select="signOut">{{ t('auth.signOut') }}</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
    <SidebarInset>
      <header class="flex h-14 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger class="-ml-1" :aria-label="t('common.toggleSidebar')" />
        <Separator orientation="vertical" class="mr-2 h-4" />
        <div class="flex flex-1 items-center gap-2 text-sm text-muted-foreground">
          <span>{{ t('nav.workspace') }}</span><span>/</span><span class="text-foreground">{{ t('nav.overview') }}</span>
        </div>
        <div class="flex items-center gap-2">
          <GlobalSearch :manifests="resourceManifests" />
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="ghost" size="sm" :aria-label="t('common.languageSwitcher')">
                <Globe2 data-icon="inline-start" aria-hidden="true" />
                <span class="hidden sm:inline">{{ locale === 'zh-CN' ? t('common.languageZh') : t('common.languageEn') }}</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" class="w-44">
              <DropdownMenuLabel>{{ t('common.languageSwitcher') }}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem @select="changeLocale('zh-CN')">
                <Check v-if="locale === 'zh-CN'" aria-hidden="true" />
                <span v-else class="size-4" aria-hidden="true" />
                {{ t('common.languageZh') }}
              </DropdownMenuItem>
              <DropdownMenuItem @select="changeLocale('en')">
                <Check v-if="locale === 'en'" aria-hidden="true" />
                <span v-else class="size-4" aria-hidden="true" />
                {{ t('common.languageEn') }}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Badge :variant="props.systemStatus === 'ok' ? 'secondary' : 'outline'">{{ props.systemStatus === 'ok' ? t('header.operational') : t('health.unavailable') }}</Badge>
        </div>
      </header>
      <slot />
    </SidebarInset>
  </SidebarProvider>
</template>
