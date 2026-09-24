import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import { namespacesForResourceRoute } from './router/resource-routes';
import { adminRouteRecords } from './router/routes';
import { adminLoginPath, adminPath, safeAdminRedirect } from './router/paths';
import { clearAccessToken, getAccessToken } from './core/api/auth';
import { clearCurrentUser, ensureCurrentUser, hasPermission } from './core/permissions';
import { i18n, loadLocaleMessages, localeFromStorage, sharedAdminNamespaces, type LocaleNamespace } from './locales';
import './styles.css';

const namespaceForRoute = (path: string): LocaleNamespace[] => {
  const resourceNamespaces = namespacesForResourceRoute(path)
  if (resourceNamespaces) return resourceNamespaces
  if (path === adminLoginPath()) return ['common', 'shell', 'auth']
  if (path === adminPath('/')) return ['common', 'shell', 'dashboard']
  if (path === adminPath('/tasks')) return ['common', 'shell', 'tasks']
  if (path === adminPath('/audit')) return ['common', 'shell', 'audit']
  if (path === adminPath('/settings')) return ['common', 'shell', 'settings']
  if (path === adminPath('/introspection')) return ['common', 'shell', 'introspection']
  if (path === adminPath('/generator')) return ['common', 'shell', 'generator', 'users', 'roles']
  if (path === adminPath('/modules')) return ['common', 'shell', 'modules', 'users', 'roles']
  if (path === adminPath('/openapi-browser')) return ['common', 'shell', 'openapi']
  if (path === adminPath('/permissions')) return ['common', 'shell', 'permissions']
  return ['common', 'shell', 'placeholder']
}

const router = createRouter({
  history: createWebHistory(),
  routes: adminRouteRecords,
});
router.beforeEach(async (to) => {
  await loadLocaleMessages(i18n.global.locale.value as 'zh-CN' | 'en', [...new Set([...namespaceForRoute(to.path), ...sharedAdminNamespaces])] as LocaleNamespace[]);
  if (to.path === adminLoginPath() && getAccessToken()) return adminPath('/');
  if (to.meta.public) return true;
  if (to.meta.requiresAuth && !getAccessToken()) return { path: adminLoginPath(), query: { redirect: safeAdminRedirect(to.fullPath) } };
  try {
    await ensureCurrentUser();
  } catch {
    clearAccessToken();
    clearCurrentUser();
    return { path: adminLoginPath(), query: { redirect: safeAdminRedirect(to.fullPath) } };
  }
  if (typeof to.meta.permission === 'string' && !hasPermission(to.meta.permission)) return '/';
  return true;
});

const initialLocale = localeFromStorage();
i18n.global.locale.value = initialLocale;

async function bootstrap(): Promise<void> {
  await loadLocaleMessages(initialLocale, [...new Set([...namespaceForRoute(window.location.pathname), ...sharedAdminNamespaces])] as LocaleNamespace[]);
  createApp(App).use(createPinia()).use(router).use(i18n).mount('#app');
}

void bootstrap();



