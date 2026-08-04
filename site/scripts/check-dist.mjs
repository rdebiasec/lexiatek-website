import { access, readFile } from 'fs/promises'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dirname = dirname(fileURLToPath(import.meta.url))
const distDir = resolve(__dirname, '../dist')

const requiredFiles = ['index.html', 'sitemap.xml', 'robots.txt', 'favicon.svg']

async function exists(path) {
  try {
    await access(path)
    return true
  } catch {
    return false
  }
}

async function main() {
  const missing = []
  for (const file of requiredFiles) {
    if (!(await exists(resolve(distDir, file)))) missing.push(file)
  }

  if (missing.length) {
    console.error('check-dist: missing files in dist/:')
    missing.forEach((file) => console.error(`  - ${file}`))
    process.exit(1)
  }

  const home = await readFile(resolve(distDir, 'index.html'), 'utf8')
  if (!home.includes('application/ld+json')) {
    console.error('check-dist: index.html missing JSON-LD')
    process.exit(1)
  }
  if (!home.includes('canonical')) {
    console.error('check-dist: index.html missing canonical')
    process.exit(1)
  }
  if (!home.includes('Content-Security-Policy')) {
    console.error('check-dist: index.html missing Content-Security-Policy')
    process.exit(1)
  }
  if (!home.includes('form-action')) {
    console.error('check-dist: CSP missing form-action')
    process.exit(1)
  }

  console.log(`check-dist: OK (${requiredFiles.length} required files present)`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
