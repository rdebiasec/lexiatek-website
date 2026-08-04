# LexiaTek — Deployment

> **Agent note — "deploy" terminology:** When the user says **"deploy"** in casual conversation about this template, clarify whether they mean **local dev** (`cd site && npm run dev` → http://localhost:5195/) or **GitHub Pages production**. Never push to GitHub or production without explicit approval.

## Environment map

| Environment | URL | How it runs |
|-------------|-----|-------------|
| **Dev (local)** | http://localhost:5195/ | `cd site && npm run dev` |
| **Prod (GitHub Pages)** | https://rdebiasec.github.io/lexiatek-website/ | Push to `main` → GitHub Actions → Pages |
| **Local folder** | `/Users/ricardodebiase/Documents/lexiatek-website` | Única carpeta de trabajo |
| **GitHub repo** | `lexiatek-website` | https://github.com/rdebiasec/lexiatek-website |

There is **no separate staging Pages** environment in this phase. Prod-like checks locally:

```bash
cd site
npm run build
npm run preview
```

## Local development

```bash
cd site
npm install   # once
npm run dev
```

Open **http://localhost:5195/** (port 5195, fixed to avoid conflicts with Pixel on 5180).

### Lead form (Formspree)

Until `VITE_FORMSPREE_FORM_ID` is set, submit shows a clear error — never fake success.

When ready:

1. Create a form at https://formspree.io
2. Set `VITE_FORMSPREE_FORM_ID` in `site/.env` (local)
3. Add the same value as Actions secret `VITE_FORMSPREE_FORM_ID`
4. Smoke-test the contact form

## Hierarchy (Pixel-aligned)

```
lexiatek-website/                   # carpeta local (única)
├── .github/
│   ├── dependabot.yml
│   └── workflows/
│       ├── deploy.yml
│       └── mirror-backup.yml
├── .gitignore
├── README.md
├── deploy2github.sh
└── site/
    ├── .env.example
    ├── .gitignore
    ├── DEPLOY.md
    ├── index.html
    ├── package.json
    ├── vite.config.js
    ├── public/
    ├── scripts/
    └── src/
```

## First-time GitHub publish

```bash
# From repo root (preferred with gh CLI):
gh repo create lexiatek-website --public --source=. --remote=origin --push

# Or:
./deploy2github.sh
```

Then: **Settings → Pages → Source: GitHub Actions**.

Without a custom domain, the workflow sets `VITE_BASE_PATH=/lexiatek-website/`.

When you have a domain, add `site/public/CNAME` and the workflow switches to `/`.

## Security notes

- CSP + Referrer-Policy + Permissions-Policy injected by `scripts/generate-seo.mjs`
- `check-dist.mjs` fails the build if CSP / canonical / JSON-LD are missing
- CI: `npm audit --audit-level=high`, SHA-pinned Actions
- Form honeypot `_gotcha`; Formspree ID validated client-side
- True HTTP headers (HSTS, X-Frame-Options) need Cloudflare Transform Rules (manual)

## Disaster recovery (Pixel pattern)

- Private mirror: [`lexiatek-website-backup`](https://github.com/rdebiasec/lexiatek-website-backup)
- Workflow: `.github/workflows/mirror-backup.yml` on every push to `main`
- Secret: `BACKUP_GITHUB_TOKEN` (configured)

## Rollback

Redeploy previous commit via `workflow_dispatch` or revert on `main`.
