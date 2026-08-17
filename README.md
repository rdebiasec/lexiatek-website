# LexiaTek Website

Carpeta: `/Users/ricardodebiase/Documents/lexiatek-website`  
Repo: https://github.com/rdebiasec/lexiatek-website  
Marca / SEO: **https://lexiatek.com** (www redirige al apex cuando el DNS esté listo)  
Hosting primario (Render Static): https://lexiatek-site.onrender.com/  
Hosting legacy (GitHub Pages, hasta migrar DNS): https://rdebiasec.github.io/lexiatek-website/

## Quick start

```bash
cd site
npm install
npm run dev
```

→ http://localhost:5195/

## Producto

| Pieza | Detalle |
|-------|---------|
| Landing | Vite + Aegis visual + CSP |
| Form leads | HubSpot Forms API (no Formspree) |
| Chat intake | Widget → API en Render (`intake-api/`) |
| Legales | `privacidad.html`, `terminos.html`, `tratamiento-datos.html` |
| WhatsApp CTA | Placeholder hasta configurar número |

Ver [`site/DEPLOY.md`](site/DEPLOY.md) y [`intake-api/HUBSPOT_SETUP.md`](intake-api/HUBSPOT_SETUP.md).
