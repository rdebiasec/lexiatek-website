# Checklist HubSpot (hacer una vez en tu portal Starter)

Seat: `ricardo.debiase@dbx-solutions.com`

## 1. Propiedades de Contacto

Settings → Data Management → Properties → Create property (Contact):

| Label | Internal name | Type |
|-------|---------------|------|
| Tipo cliente | `tipo_cliente` | Dropdown: `natural`, `juridica` |
| Rol LexiaTek | `rol_lexiatek` | Dropdown: `victima`, `investigado`, `familiar`, `otro` |
| WhatsApp | `whatsapp` | Single-line text |
| Resumen consulta | `resumen_consulta` | Multi-line text |
| Consentimiento datos | `consentimiento_datos` | Checkbox / boolean |
| Fuente | `fuente` | Dropdown: `widget_agente`, `form`, `whatsapp` |

Docs: https://knowledge.hubspot.com/properties/create-and-edit-properties

## 2. Pipeline Deal — Asesoría inicial

Settings → Objects → Deals → Pipelines → Create pipeline `Asesoria inicial` con etapas:

1. Nuevo  
2. Contactado  
3. Agendado  
4. Cerrado ganado  
5. Cerrado perdido  

Docs: https://knowledge.hubspot.com/object-settings/set-up-and-customize-pipelines

Anota el **pipeline ID** y stage IDs (o deja que la API use el pipeline default si solo hay uno).

## 3. Private App

Settings → Integrations → Private Apps → Create:

Scopes mínimos:

- `crm.objects.contacts.read`
- `crm.objects.contacts.write`
- `crm.objects.companies.read`
- `crm.objects.companies.write`
- `crm.objects.deals.read`
- `crm.objects.deals.write`
- `crm.objects.notes.write` (o `crm.objects.contacts.write` + notes según UI actual)

Docs: https://developers.hubspot.com/docs/guides/apps/private-apps/overview

Copia el access token → `HUBSPOT_ACCESS_TOKEN` en `intake-api/.env` (nunca al git).

Pon `HUBSPOT_DRY_RUN=false` cuando el token esté listo.

## 4. Workflow notify (opcional Starter)

Trigger: Contact created where `fuente` = `widget_agente`  
Action: Send internal email / notification to `ricardo.debiase@dbx-solutions.com`

## 6. Formulario web (landing — Forms API)

Además del widget, la landing envía al **HubSpot Forms API**:

1. Marketing → Forms → Create form (campos: firstname, email, phone, whatsapp, rol_lexiatek, resumen_consulta, consentimiento_datos, fuente).
2. Copiar Portal ID + Form ID → secrets `VITE_HUBSPOT_PORTAL_ID` / `VITE_HUBSPOT_FORM_ID`.
3. Docs: https://developers.hubspot.com/docs/api-reference/legacy/forms-v3-legacy/guide

No usar Formspree.

## 5. Smoke

```bash
cd intake-api
cp .env.example .env   # OPENAI_API_KEY + HUBSPOT_ACCESS_TOKEN
pip install -e .       # Python ≥3.12
uvicorn src.main:app --reload --port 8787
```

Landing `:5195` → widget + form HubSpot → Contact en CRM.
