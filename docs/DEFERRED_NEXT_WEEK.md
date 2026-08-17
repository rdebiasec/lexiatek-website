# Lista diferida — próxima semana (no olvidar)

Última actualización: 2026-08-17  
Estado: Cloudflare/WAF **aún diferido**; varias remediaciones de API/sitio ya en prod (`0829e0d`+).

## Semana siguiente — Edge / Cloudflare

- [ ] Evaluar Cloudflare delante de `lexiatek.com` (cuando el DNS/TLS estén correctos)
- [ ] WAF + Bot Fight / rate limit en edge
- [ ] Headers HTTP reales: HSTS, `frame-ancestors`, `X-Content-Type-Options`
- [ ] Protección DDoS básica del sitio y, si aplica, proxy hacia la API Render
- [ ] Checklist post-cambio DNS (TTL, www→apex, certificado TLS)
- [ ] **Verificado 2026-08-17:** NS Cloudflare; apex aún → IPs GitHub Pages (TLS roto/404). Sitio preferido: `https://lexiatek-site.onrender.com`. Arreglar origen ANTES del WAF.

**Por qué importa:** Cloudflare Docs (SSL Full strict, WAF); OWASP Secure Headers Project; NIST SP 800-52 Rev. 2 (TLS).

## Relacionado

- [x] Redeploy intake-api endurecido (`version` 0.3.0 en `/health`) — 2026-08-17
- [x] Gates WhatsApp en código: verify token + `X-Hub-Signature-256` (`/whatsapp`) — falta configurar secretos Meta en Render
- [x] Sitio Render Static live (`lexiatek-site`) + nanoid CI fix
- [ ] Apuntar `lexiatek.com` al origen Render Static (y luego desactivar Pages)
- [ ] Disco persistente o Postgres para `usage.jsonl` (hoy: `./data/usage.jsonl` efímero)
- [ ] Tokens reales OpenAI + HubSpot; salir de dry-run cuando listo
- [ ] `WHATSAPP_VERIFY_TOKEN` + `META_APP_SECRET` en Render + webhook en Meta
- [ ] Staging explícito (API dry-run + preview del sitio)
- [ ] Alertas de gasto OpenAI + uptime
- [ ] Decisión final SLO / plan Render (costos)

## Canales

- Webchat (`/v1/chat` + widget) — live endurecido
- WhatsApp — endpoint listo; onboarding Meta pendiente
