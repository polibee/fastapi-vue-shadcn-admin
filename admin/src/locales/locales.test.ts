import { describe, expect, it } from 'vitest'
import enAuth from './en/auth.json'
import enCommon from './en/common.json'
import enDashboard from './en/dashboard.json'
import enShell from './en/shell.json'
import zhAuth from './zh-CN/auth.json'
import zhCommon from './zh-CN/common.json'
import zhDashboard from './zh-CN/dashboard.json'
import zhShell from './zh-CN/shell.json'

function keys(value: unknown): string[] {
  return Object.keys(value as Record<string, unknown>).sort()
}

describe('locale namespaces', () => {
  it('keeps the default language namespace structure aligned', () => {
    expect(keys(zhCommon)).toEqual(keys(enCommon))
    expect(keys(zhShell)).toEqual(keys(enShell))
    expect(keys(zhAuth)).toEqual(keys(enAuth))
    expect(keys(zhDashboard)).toEqual(keys(enDashboard))
  })

  it('keeps the admin identity neutral in every language', () => {
    expect(JSON.stringify(zhDashboard)).not.toMatch(/hongbo/i)
    expect(JSON.stringify(enDashboard)).not.toMatch(/hongbo/i)
    expect(JSON.stringify(zhCommon)).toContain('admin')
    expect(JSON.stringify(enCommon)).toContain('admin')
  })
})
