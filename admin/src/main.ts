import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import DashboardPage from './components/admin/DashboardPage.vue';
import ModulePlaceholder from './components/admin/ModulePlaceholder.vue';
import LoginPage from './components/admin/LoginPage.vue';
import AuditPage from './components/admin/AuditPage.vue';
import TasksPage from './components/admin/TasksPage.vue';
import SettingsPage from './components/admin/SettingsPage.vue';
import IntrospectionPage from './components/admin/IntrospectionPage.vue';
import GeneratorPage from './components/admin/GeneratorPage.vue';
import ModuleRegistryPage from './components/admin/ModuleRegistryPage.vue';
import OpenApiExplorerPage from './components/admin/OpenApiExplorerPage.vue';
import PermissionsPage from './components/admin/PermissionsPage.vue';
import { namespacesForResourceRoute, resourceRoutes } from './router/resource-routes';
import { clearAccessToken, getAccessToken } from './core/api/auth';
import { clearCurrentUser, ensureCurrentUser, hasPermission } from './core/permissions';
import { i18n, loadLocaleMessages, localeFromStorage, type LocaleNamespace } from './locales';
import './styles.css';

const namespaceForRoute = (path: string): LocaleNamespace[] => {
  const resourceNamespaces = namespacesForResourceRoute(path)
  if (resourceNamespaces) return resourceNamespaces
  if (path === '/login') return ['common', 'shell', 'auth']
  if (path === '/') return ['common', 'shell', 'dashboard']
  if (path === '/tasks') return ['common', 'shell', 'tasks']
  if (path === '/audit') return ['common', 'shell', 'audit']
  if (path === '/settings') return ['common', 'shell', 'settings']
  if (path === '/introspection') return ['common', 'shell', 'introspection']
  if (path === '/generator') return ['common', 'shell', 'generator', 'users', 'roles']
  if (path === '/modules') return ['common', 'shell', 'modules', 'users', 'roles']
  if (path === '/openapi-browser') return ['common', 'shell', 'openapi']
  if (path === '/permissions') return ['common', 'shell', 'permissions']
  return ['common', 'shell', 'placeholder']
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginPage, meta: { public: true } },
    { path: '/', component: DashboardPage, meta: { requiresAuth: true } },
    { path: '/activity', component: ModulePlaceholder, props: { titleKey: 'nav.activity' }, meta: { requiresAuth: true } },
    { path: '/tasks', component: TasksPage, meta: { requiresAuth: true, permission: 'tasks.view' } },
    ...resourceRoutes,
    { path: '/audit', component: AuditPage, meta: { requiresAuth: true, permission: 'audit.view' } },
    { path: '/settings', component: SettingsPage, meta: { requiresAuth: true } },
    { path: '/introspection', component: IntrospectionPage, meta: { requiresAuth: true, permission: 'users.view' } },
    { path: '/generator', component: GeneratorPage, meta: { requiresAuth: true, permission: 'users.view' } },
    { path: '/modules', component: ModuleRegistryPage, meta: { requiresAuth: true, permission: 'users.view' } },
    { path: '/openapi-browser', component: OpenApiExplorerPage, meta: { requiresAuth: true, permission: 'users.view' } },
    { path: '/permissions', component: PermissionsPage, meta: { requiresAuth: true, permission: 'roles.view' } },
  ],
});
router.beforeEach(async (to) => {
  await loadLocaleMessages(i18n.global.locale.value as 'zh-CN' | 'en', namespaceForRoute(to.path));
  if (to.path === '/login' && getAccessToken()) return '/';
  if (to.meta.public) return true;
  if (to.meta.requiresAuth && !getAccessToken()) return { path: '/login', query: { redirect: to.fullPath } };
  try {
    await ensureCurrentUser();
  } catch {
    clearAccessToken();
    clearCurrentUser();
    return { path: '/login', query: { redirect: to.fullPath } };
  }
  if (typeof to.meta.permission === 'string' && !hasPermission(to.meta.permission)) return '/';
  return true;
});

const initialLocale = localeFromStorage();
i18n.global.locale.value = initialLocale;

async function bootstrap(): Promise<void> {
  await loadLocaleMessages(initialLocale, namespaceForRoute(window.location.pathname));
  createApp(App).use(createPinia()).use(router).use(i18n).mount('#app');
}

void bootstrap();
