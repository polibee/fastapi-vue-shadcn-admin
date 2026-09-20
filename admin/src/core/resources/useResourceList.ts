import { computed, ref } from 'vue'

export type ResourceListQuery = { offset: number; limit: number; sortBy: string; sortOrder: 'asc' | 'desc' }
export type ResourceListResponse<T> = { items: T[]; total: number }
export type ResourceListLoader<T> = (query: ResourceListQuery) => Promise<ResourceListResponse<T>>

export function useResourceList<T>(loader: ResourceListLoader<T>, pageSize = 10) {
  const items = ref<T[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref(false)
  const page = ref(1)
  const sortBy = ref('id')
  const sortOrder = ref<'asc' | 'desc'>('asc')
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

  async function load(): Promise<void> {
    loading.value = true
    error.value = false
    try {
      const result = await loader({ offset: (page.value - 1) * pageSize, limit: pageSize, sortBy: sortBy.value, sortOrder: sortOrder.value })
      items.value = result.items
      total.value = result.total
    } catch {
      error.value = true
    } finally {
      loading.value = false
    }
  }

  async function reset(): Promise<void> {
    page.value = 1
    await load()
  }

  async function changePage(nextPage: number): Promise<void> {
    page.value = Math.min(Math.max(1, nextPage), totalPages.value)
    await load()
  }

  async function setSort(nextSortBy: string, nextSortOrder: 'asc' | 'desc'): Promise<void> {
    sortBy.value = nextSortBy
    sortOrder.value = nextSortOrder
    await reset()
  }

  return { items, total, loading, error, page, pageSize, totalPages, sortBy, sortOrder, load, reset, changePage, setSort }
}
