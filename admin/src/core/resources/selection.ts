import { computed, ref } from 'vue'

export function useResourceSelection() {
  const selectedIds = ref<number[]>([])
  const selectedCount = computed(() => selectedIds.value.length)

  function toggle(id: number): void {
    selectedIds.value = selectedIds.value.includes(id)
      ? selectedIds.value.filter((selected) => selected !== id)
      : [...selectedIds.value, id]
  }

  function toggleAll(ids: number[]): void {
    selectedIds.value = selectedIds.value.length === ids.length ? [] : [...ids]
  }

  function clear(): void {
    selectedIds.value = []
  }

  function isSelected(id: number): boolean {
    return selectedIds.value.includes(id)
  }

  return { selectedIds, selectedCount, toggle, toggleAll, clear, isSelected }
}
