import type { Component } from 'vue'
import type { ResourceFieldType } from './types'

export type FieldRenderer = Component

class FieldRendererRegistry {
  private readonly renderers = new Map<ResourceFieldType, FieldRenderer>()

  register(type: ResourceFieldType, renderer: FieldRenderer): void {
    this.renderers.set(type, renderer)
  }

  get(type: ResourceFieldType): FieldRenderer | undefined {
    return this.renderers.get(type)
  }

  has(type: ResourceFieldType): boolean {
    return this.renderers.has(type)
  }
}

export const fieldRendererRegistry = new FieldRendererRegistry()
