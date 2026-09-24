import { describe, expect, it } from 'vitest'
import config from '../vite.config'

describe('development API proxy', () => {
  it('serves the frontend as an SPA with root-safe assets for nested admin routes', () => {
    expect(config.appType).toBe('spa')
    expect(config.base).toBe('/')
  })

  it('proxies Scalar documentation to FastAPI instead of the SPA fallback', () => {
    const proxy = config.server?.proxy as Record<string, unknown>
    expect(proxy['/docs']).toBe('http://127.0.0.1:8012')
  })

  it('keeps every backend entry point on the same configurable API target', () => {
    const proxy = config.server?.proxy as Record<string, unknown>
    expect(new Set(Object.values(proxy))).toEqual(new Set(['http://127.0.0.1:8012']))
  })
})
