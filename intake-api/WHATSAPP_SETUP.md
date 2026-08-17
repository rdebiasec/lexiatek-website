# Checklist WhatsApp API (Arquitectura A — humano + conector → HubSpot Starter)

Aprobado: 9 ago 2026 · Sprint: **A** (agente WA = fase 2, no aquí).

Seat HubSpot: `ricardo.debiase@dbx-solutions.com`

## 0. Privacidad (antes de go-live)

Checklist corto Ley **1581** + **2300** (canal WhatsApp):

- [ ] Finalidad del canal documentada: asesoría inicial / updates operativos (no marketing agresivo).
- [ ] Opt-in claro: ciudadano inicia por `wa.me` o marca consentimiento web que incluye contacto por WhatsApp.
- [ ] Aviso de privacidad y autorización mencionan WhatsApp + Meta/BSP como encargados.
- [ ] No pedir ni guardar evidencias / hechos sensibles en logs del BSP ni notas HubSpot largas.
- [ ] Retención: alinear con privacidad LexiaTek; borrar hilos de prueba.
- [ ] Templates Meta solo utility (bienvenida / update / recordatorio) con opt-in.

Docs legales en site: `privacidad.html`, `tratamiento-datos.html`.

## 1. Número Business LexiaTek

- [ ] Número dedicado (no celular personal).
- [ ] Formato CTA: `https://wa.me/57XXXXXXXXXX` (sin `+` ni espacios).
- [ ] Anotar el número E.164 completo: `+57…`

## 2. Meta Business Manager + Cloud API

1. [developers.facebook.com](https://developers.facebook.com/) → Create App → tipo Business / con producto **WhatsApp**.
2. Conectar o crear **WhatsApp Business Account (WABA)**.
3. Añadir / verificar el número Business (o usar número de prueba primero).
4. En **WhatsApp → API Setup** copiar:
   - Phone Number ID
   - WhatsApp Business Account ID
5. Crear **System User** (Business Settings) → Generate token con:
   - `whatsapp_business_messaging`
   - `whatsapp_business_management`
6. Copiar **App Secret** (App settings → Basic) para firma de webhooks.

Docs:

- https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/
- https://developers.facebook.com/documentation/business-messaging/whatsapp/access-tokens/
- https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks/

## 3. Path: BSP (recomendado A) vs Cloud API directo

| Path | Cuándo | Inbox | Sync HubSpot |
|------|--------|-------|--------------|
| **BSP** (Wati / Respond.io / TimelinesAI / similar) | Sprint A — menos código | Incluido | Conector nativo o Zapier-like |
| **Cloud API directo** | Si quieres control total en `intake-api` | Tú lo construyes | Webhook → CRM tools |

Elegido para LexiaTek sprint A: **BSP + conector HubSpot Starter** (no Professional nativo).

Checklist BSP:

- [ ] Alta cuenta BSP con el WABA / número LexiaTek.
- [ ] Invitar operadores (abogado + coordinación).
- [ ] Activar integración HubSpot → Contact `fuente=whatsapp` (o mapeo equivalente).
- [ ] Probar inbound: mensaje test → aparece en inbox → Contact en portal.

## 4. Plantillas Meta (utility, ES-CO)

En WhatsApp Manager → Message templates (o vía BSP):

| Uso | Categoría | Ejemplo nombre |
|-----|-----------|----------------|
| Bienvenida post primer contacto | Utility | `lexiatek_bienvenida` |
| Update de etapa / “qué sigue” | Utility | `lexiatek_update_etapa` |
| Recordatorio cita o documento | Utility | `lexiatek_recordatorio` |

- [ ] Idioma `es` o `es_CO` según UI Meta.
- [ ] Esperar status **APPROVED** antes de enviar.
- [ ] Regla operativa: borrador IA → aprueba abogado → envío.

Docs: https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates

## 5. Secrets (nunca al git)

### Landing (CTA)

`site/.env` y GitHub Actions secret:

```bash
VITE_WHATSAPP_URL=https://wa.me/57XXXXXXXXXX
```

Redeploy Pages tras setear el secret.

### Si más adelante usas Cloud API en intake-api (fase 2)

```bash
WHATSAPP_TOKEN=...                 # System User
WHATSAPP_PHONE_NUMBER_ID=...
WHATSAPP_BUSINESS_ACCOUNT_ID=...
WHATSAPP_VERIFY_TOKEN=...          # string aleatorio tuyo
META_APP_SECRET=...                # firma X-Hub-Signature-256
```

No hace falta para el sprint A con BSP.

## 6. HubSpot (CRM del canal)

Ya definido en [`HUBSPOT_SETUP.md`](./HUBSPOT_SETUP.md):

- Propiedad `whatsapp`
- Dropdown `fuente` incluye valor `whatsapp`
- Workflow opcional: Contact created `fuente=whatsapp` → email a seat

- [ ] Confirmar props creadas en el portal.
- [ ] Smoke: Contact con `fuente=whatsapp` visible para el seat.

## 7. Smoke end-to-end (Arquitectura A)

1. CTA landing abre chat real (ya no “próximamente”).
2. Ciudadano escribe → inbox BSP.
3. Contact en HubSpot con teléfono/WhatsApp y `fuente=whatsapp` (o nota del hilo).
4. Template utility aprobado entrega solo con opt-in / ventana válida.
5. Ningún secret en frontend salvo `VITE_WHATSAPP_URL` (público por diseño = wa.me).

## 8. Webhook en intake-api (gates listos; agente = fase 2)

Código: `GET/POST /whatsapp` en `intake-api` con:

- [ ] `WHATSAPP_VERIFY_TOKEN` (handshake Meta)
- [ ] `META_APP_SECRET` → valida `X-Hub-Signature-256`
- [ ] No loguear texto de mensajes / evidencias (solo conteo de entries)

Fuera aún:

- Agente OpenAI por canal WA (`fuente=whatsapp`)
- HubSpot Professional WhatsApp nativo (descartado)

Docs firma: https://developers.facebook.com/docs/graph-api/webhooks/getting-started#verification-requests

## Docs oficiales

| Tema | URL |
|------|-----|
| Cloud API | https://developers.facebook.com/docs/whatsapp/cloud-api/ |
| Get started | https://developers.facebook.com/docs/whatsapp/cloud-api/get-started/ |
| Webhooks | https://developers.facebook.com/docs/whatsapp/cloud-api/guides/set-up-webhooks/ |
| Messages | https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages |
| Templates | https://developers.facebook.com/docs/whatsapp/business-management-api/message-templates |
| Pricing | https://developers.facebook.com/docs/whatsapp/pricing/ |
