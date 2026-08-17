# LexiaTek — Deployment

> **Agent note — "deploy":** clarify **local** (`npm run dev` → :5195) vs **prod**. Never push without approval.

## Environment map (verified 2026-08-17)

| Environment | URL | How |
|-------------|-----|-----|
| **Dev** | http://localhost:5195/ | `cd site && npm run dev` |
| **Prod sitio (GitHub Pages — aún activo)** | https://rdebiasec.github.io/lexiatek-website/ | Workflow `Site CI and Pages` |
| **Prod sitio (Render Static — preferido)** | https://lexiatek-site.onrender.com | Auto-deploy desde `main` / `site/` |
| **SEO / marca** | https://lexiatek.com | DNS/TLS deben apuntar al origen canónico elegido (hoy: roto si apunta mal a Pages) |
| **Intake API + webchat + WA webhook gates** | https://lexiatek-intake-api.onrender.com | `intake-api/render.yaml` · health `/health` |

## Decisión de origen (importante)

1. **API siempre en Render** (`lexiatek-intake-api`).
2. **Sitio:** Render Static (`lexiatek-site`) es el destino preferido para unificar prod en Render.
   - Build: `cd site && npm ci && npm run build` · Publish: `site/dist`
   - Vite va en `dependencies` (no solo `devDependencies`): Render usa `NODE_ENV=production` y omite devDeps.
   - Env: `VITE_BASE_PATH=/`, `VITE_INTAKE_API_URL=https://lexiatek-intake-api.onrender.com`, más HubSpot Vite secrets en el dashboard.
3. **GitHub Pages** sigue desplegando como fallback hasta que `lexiatek.com` tenga TLS correcto hacia el origen elegido; luego se puede deshabilitar Pages en GitHub Settings.
4. Cloudflare WAF: ver [`docs/DEFERRED_NEXT_WEEK.md`](../docs/DEFERRED_NEXT_WEEK.md).

## Leads (HubSpot)

1. HubSpot form + Portal ID / Form GUID.
2. Local: `site/.env` → `VITE_HUBSPOT_*`
3. GitHub Actions secrets + Render Static env vars (mismos nombres).
4. API: `HUBSPOT_ACCESS_TOKEN`, `HUBSPOT_DRY_RUN=false` en Render para leads reales.

Docs: https://developers.hubspot.com/docs/api-reference/legacy/forms-v3-legacy/guide

## Widget intake (Render)

```bash
cd intake-api
cp .env.example .env
# OPENAI_API_KEY, HUBSPOT_ACCESS_TOKEN, USAGE_ADMIN_TOKEN (fuerte)
# ALLOW_INSECURE_DEFAULTS=true solo en local
```

Set `VITE_INTAKE_API_URL=https://lexiatek-intake-api.onrender.com` en build del sitio.

Checklist CRM: [`intake-api/HUBSPOT_SETUP.md`](../intake-api/HUBSPOT_SETUP.md)

## WhatsApp (deployment final)

Checklist: [`intake-api/WHATSAPP_SETUP.md`](../intake-api/WHATSAPP_SETUP.md)

- Sprint A: BSP + HubSpot (humano).
- Gates en API (fase 2 listos en código): `GET/POST /whatsapp` con `hub.verify_token` y `X-Hub-Signature-256` (`META_APP_SECRET`).
- CTA: `VITE_WHATSAPP_URL=https://wa.me/57XXXXXXXXXX`

## Dominio lexiatek.com

Antes de WAF:

1. Elegir origen: Render Static **o** GitHub Pages (no ambos sin redirect claro).
2. Cloudflare DNS → ese origen; SSL mode **Full (strict)**.
3. Si Pages: `site/public/CNAME` + `VITE_BASE_PATH=/`.
4. Si Render Static: custom domain en el dashboard del static site.

## Security (código)

- Rate limit + hard cap tokens + admin Bearer-only + session TTL
- CSP meta + honeypot + HubSpot Forms
- `npm audit --audit-level=high` + `pip-audit` en CI
- Disco Render `/var/data` para `usage.jsonl`
- Mirror privado: `BACKUP_GITHUB_TOKEN`
