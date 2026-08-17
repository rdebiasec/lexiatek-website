# Lista diferida — próxima semana (no olvidar)

Última actualización: 2026-08-16  
Estado: **NO ejecutar aún** (después de la auditoría fases 0–3).

## Semana siguiente — Edge / Cloudflare

- [ ] Evaluar Cloudflare delante de `lexiatek.com` (cuando el DNS/TLS estén correctos)
- [ ] WAF + Bot Fight / rate limit en edge
- [ ] Headers HTTP reales: HSTS, `frame-ancestors`, `X-Content-Type-Options`
- [ ] Protección DDoS básica del sitio y, si aplica, proxy hacia la API Render
- [ ] Checklist post-cambio DNS (TTL, www→apex, certificado TLS)
- [ ] **Verificado 2026-08-16:** NS ya son Cloudflare, pero apex apunta a IPs GitHub Pages con TLS roto/404 — arreglar origen ANTES del WAF

**Por qué importa:** Cloudflare Docs (SSL Full strict, WAF); OWASP Secure Headers Project; NIST SP 800-52 Rev. 2 (TLS). GitHub Pages y Render dan TLS en su dominio, pero el apex de marca debe coincidir con el origen real.

## Relacionado (después de auditoría, no ahora)

- [ ] Decisión final SLO / plan Render (tras ver costos en el informe)
- [ ] Staging explícito (API dry-run + preview del sitio)
- [ ] Disco persistente o Postgres para `usage.jsonl`
- [ ] Gates WhatsApp: firma `X-Hub-Signature-256`, retención, no-evidencias
- [ ] Alertas de gasto OpenAI + uptime

## Canales en alcance del despliegue final

- Webchat (`/v1/chat` + widget) — live / hardening
- WhatsApp Business (Arquitectura A → fase agente) — parte del **deployment final**; auditar como superficie de riesgo aunque el webhook aún no esté en código
