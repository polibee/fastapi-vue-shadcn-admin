const alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@#$%^&*'

export function generateSecurePassword(length = 16): string {
  const size = Math.max(12, length)
  const values = new Uint32Array(size)
  crypto.getRandomValues(values)
  return Array.from(values, (value) => alphabet[value % alphabet.length]).join('')
}
