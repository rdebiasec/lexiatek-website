# LexiaTek — Deployment

> **Agent note — "deploy":** clarify **local** (`npm run dev` → :5195) vs **GitHub Pages**. Never push without approval.

## Environment map

| Environment | URL | How |
|-------------|-----|-----|
| **Dev** | http://localhost:5195/ | `cd site && npm run dev` |
| **Prod (hosting hoy)** | https://rdebiasec.github.io/lexiatek-website/ | Push `main` → Actions → Pages |
| **SEO / marca** | https://lexiatek.com (www → apex cuando DNS esté listo) | Canonical/OG ya apuntan aquí |
| **Intake API** | Render (`lexiatek-intake-api`) | `intake-api/render.yaml` |

## Leads (HubSpot — sin Formspree)

1. En HubSpot Starter: crear form con campos alineados (`firstname`, `email`, `phone`, `whatsapp`, `rol_lexiatek`, `resumen_consulta`, `consentimiento_datos`, `fuente`).
2. Copiar **Portal ID** y **Form GUID**.
3. Local: `site/.env` → `VITE_HUBSPOT_PORTAL_ID` + `VITE_HUBSPOT_FORM_ID`
4. GitHub Actions secrets: mismos nombres.
5. Workflow notify a `ricardo.debiase@dbx-solutions.com`.

Docs form submit API: https://developers.hubspot.com/docs/api-reference/legacy/forms-v3-legacy/guide

## Widget intake (Render)

```bash
cd intake-api
cp .env.example .env   # OPENAI_API_KEY, HUBSPOT_ACCESS_TOKEN, HUBSPOT_DRY_RUN=false
# Deploy via Render blueprint or dashboard (rootDir: intake-api)
```

Set secret `VITE_INTAKE_API_URL=https://<servicio>.onrender.com` so Pages habla con Render (CSP se genera en build).

Checklist CRM: [`intake-api/HUBSPOT_SETUP.md`](../intake-api/HUBSPOT_SETUP.md)

## WhatsApp CTA

Dejar `VITE_WHATSAPP_URL` vacío → botón “WhatsApp (próximamente)” apunta a `#contacto`.  
Cuando tengas número: `https://wa.me/57XXXXXXXXXX` en secret + redeploy.

## Dominio lexiatek.com

Cuando DNS esté listo:

1. Añadir `site/public/CNAME` con `lexiatek.com`
2. Configurar DNS + redirect `www` → apex
3. Redeploy (workflow pondrá `VITE_BASE_PATH=/`)

Hasta entonces el sitio se sirve en github.io; SEO canónico sigue siendo `https://lexiatek.com/`.

## Security

- CSP + honeypot + HubSpot Forms API
- `npm audit --audit-level=high` en CI
- Mirror privado: `BACKUP_GITHUB_TOKEN`

## Local

```bash
cd site && npm install && npm run dev
# API widget (otra terminal):
cd intake-api && .venv/bin/uvicorn src.main:app --reload --port 8787
```
