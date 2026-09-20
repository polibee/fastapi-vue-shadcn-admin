import { createI18n } from 'vue-i18n'

export type SupportedLocale = 'zh-CN' | 'en'
export type LocaleNamespace = 'common' | 'shell' | 'auth' | 'dashboard' | 'placeholder' | 'users' | 'roles' | 'audit' | 'tasks' | 'settings' | 'introspection' | 'generator' | 'modules' | 'openapi' | 'permissions'

const localeLoaders = import.meta.glob<Record<string, unknown>>('./**/*.json')

export const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en',
  messages: { 'zh-CN': {}, en: {} },
})

export async function loadLocaleMessages(locale: SupportedLocale, namespaces: LocaleNamespace[]): Promise<void> {
  const uniqueNamespaces = [...new Set(namespaces)]
  await Promise.all(uniqueNamespaces.map(async (namespace) => {
    const loader = localeLoaders[`./${locale}/${namespace}.json`]
    if (!loader) throw new Error(`Missing locale namespace: ${locale}/${namespace}`)
    const module = await loader()
    i18n.global.mergeLocaleMessage(locale, module.default ?? module)
  }))
}

export async function setLocale(locale: SupportedLocale, namespaces: LocaleNamespace[]): Promise<void> {
  await loadLocaleMessages(locale, namespaces)
  i18n.global.locale.value = locale
}

export function localeFromStorage(): SupportedLocale {
  const saved = typeof window === 'undefined' ? null : window.localStorage.getItem('admin-locale')
  return saved === 'en' || saved === 'zh-CN' ? saved : 'zh-CN'
}
