import { mkdtemp, readdir, readFile, rm } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { dirname, join, relative } from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const repoRoot = dirname(dirname(fileURLToPath(import.meta.url)))
const adminRoot = join(repoRoot, 'admin')
const generatedRoot = join(adminRoot, 'src', 'core', 'api', 'generated', 'client')
const tempRoot = await mkdtemp(join(tmpdir(), 'fastapi-admin-sdk-'))

async function filesUnder(root) {
  const entries = await readdir(root, { withFileTypes: true })
  const files = []
  for (const entry of entries) {
    const path = join(root, entry.name)
    if (entry.isDirectory()) files.push(...await filesUnder(path))
    else files.push(path)
  }
  return files
}

try {
  const result = spawnSync('pnpm', [
    'exec', 'openapi-ts',
    '-i', 'http://127.0.0.1:8012/openapi.json',
    '-o', tempRoot,
    '-c', '@hey-api/client-fetch',
  ], { cwd: adminRoot, stdio: 'inherit', shell: process.platform === 'win32' })
  if (result.status !== 0) process.exit(result.status ?? 1)

  const expected = new Set((await filesUnder(generatedRoot)).map((file) => relative(generatedRoot, file)))
  const actual = new Set((await filesUnder(tempRoot)).map((file) => relative(tempRoot, file)))
  const differences = []
  for (const path of new Set([...expected, ...actual])) {
    const expectedPath = join(generatedRoot, path)
    const actualPath = join(tempRoot, path)
    if (!existsSync(expectedPath) || !existsSync(actualPath)) {
      differences.push(path)
      continue
    }
    const [expectedContent, actualContent] = await Promise.all([readFile(expectedPath), readFile(actualPath)])
    if (!expectedContent.equals(actualContent)) differences.push(path)
  }

  if (differences.length > 0) {
    console.error(`Generated SDK is stale. Run pnpm run generate:sdk in admin/. Changed files:`)
    for (const path of differences.sort()) console.error(`- ${path}`)
    process.exitCode = 1
  } else {
    console.log('Generated SDK is up to date.')
  }
} finally {
  await rm(tempRoot, { recursive: true, force: true })
}
