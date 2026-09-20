import { describe, expect, it } from 'vitest'
import config from '../vite.config'

describe('development API proxy', () => {
  it('proxies Scalar documentation to FastAPI instead of the SPA fallback', () => {
    const proxy = config.server?.proxy as Record<string, unknown>
    expect(proxy['/docs']).toBe('http://127.0.0.1:8012')
  })
})