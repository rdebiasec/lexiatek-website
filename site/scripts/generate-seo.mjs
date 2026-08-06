import { writeFile, readFile, mkdir } from 'fs/promises'
import { dirname, resolve } from 'path'
import { fileURLToPath } from 'url'
import { COMPANY_LEGAL_NAME, META, SITE_URL } from '../src/legal/constants.js'

const __dirname = dirname(fileURLToPath(import.meta.url))
const root = resolve(__dirname, '..')
const publicDir = resolve(root, 'public')

function intakeConnectHosts() {
  const hosts = new Set([
    "'self'",
    'https://api.hsforms.com',
    'https://js.hsforms.net',
    'https://forms.hubspot.com'
  ])
  const intake = (process.env.VITE_INTAKE_API_URL || '').replace(/\/$/, '')
  if (intake.startsWith('https://') || intake.startsWith('http://')) {
    try {
      hosts.add(new URL(intake).origin)
    } catch {
      /* ignore bad URL */
    }
  }
  // Local widget only in non-production builds
  if (process.env.NODE_ENV !== 'production') {
    hosts.add('http://127.0.0.1:8787')
    hosts.add('http://localhost:8787')
  }
  return [...hosts].join(' ')
}

function buildCsp() {
  return [
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "img-src 'self' data: https:",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "script-src 'self'",
    `connect-src ${intakeConnectHosts()}`,
    "form-action 'self' https://api.hsforms.com https://forms.hubspot.com",
    "frame-ancestors 'none'",
    'upgrade-insecure-requests'
  ].join('; ')
}

function legalServiceSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'LegalService',
    name: COMPANY_LEGAL_NAME,
    url: SITE_URL,
    description: META.description,
    areaServed: {
      '@type': 'Country',
      name: 'Colombia'
    },
    availableLanguage: ['es'],
    sameAs: ['https://www.lexiatek.com']
  }
}

function buildSeoBlock() {
  const canonical = `${SITE_URL}/`
  const csp = buildCsp()
  const schema = JSON.stringify(legalServiceSchema())

  return [
    `    <meta http-equiv="Content-Security-Policy" content="${csp}" />`,
    '    <meta name="referrer" content="strict-origin-when-cross-origin" />',
    '    <meta http-equiv="Permissions-Policy" content="geolocation=(), microphone=(), camera=()" />',
    `    <link rel="canonical" href="${canonical}" />`,
    `    <link rel="alternate" href="https://www.lexiatek.com/" />`,
    `    <meta property="og:title" content="${META.title}" />`,
    `    <meta property="og:description" content="${META.description}" />`,
    `    <meta property="og:url" content="${canonical}" />`,
    '    <meta property="og:type" content="website" />',
    `    <meta property="og:site_name" content="${COMPANY_LEGAL_NAME}" />`,
    `    <meta property="og:locale" content="es_CO" />`,
    '    <meta name="twitter:card" content="summary_large_image" />',
    `    <meta name="twitter:title" content="${META.title}" />`,
    `    <meta name="twitter:description" content="${META.description}" />`,
    `    <script type="application/ld+json">${schema}</script>`
  ].join('\n')
}

async function patchHtml(fileName) {
  const indexPath = resolve(root, fileName)
  let html = await readFile(indexPath, 'utf8')
  const block = `  <!-- seo:generated -->\n${buildSeoBlock()}\n  <!-- /seo:generated -->`
  if (html.includes('<!-- seo:generated -->')) {
    html = html.replace(/<!-- seo:generated -->[\s\S]*?<!-- \/seo:generated -->/, block.trim())
  } else if (html.includes('</head>')) {
    html = html.replace('</head>', `${block}\n</head>`)
  }
  await writeFile(indexPath, html, 'utf8')
}

async function writePublicSeo() {
  await mkdir(publicDir, { recursive: true })
  await writeFile(
    resolve(publicDir, 'robots.txt'),
    `User-agent: *\nAllow: /\nSitemap: ${SITE_URL}/sitemap.xml\n`,
    'utf8'
  )
  await writeFile(
    resolve(publicDir, 'sitemap.xml'),
    `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>${SITE_URL}/</loc></url>
  <url><loc>${SITE_URL}/privacidad.html</loc></url>
  <url><loc>${SITE_URL}/terminos.html</loc></url>
  <url><loc>${SITE_URL}/tratamiento-datos.html</loc></url>
</urlset>
`,
    'utf8'
  )
}

async function main() {
  await patchHtml('index.html')
  for (const page of ['privacidad.html', 'terminos.html', 'tratamiento-datos.html']) {
    try {
      await patchHtml(page)
    } catch {
      /* page may not exist yet on first run */
    }
  }
  await writePublicSeo()
  console.log('generate-seo: CSP, OG, JSON-LD, robots, sitemap OK')
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
