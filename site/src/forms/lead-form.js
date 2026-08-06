import { CONTACT_EMAIL } from '../legal/constants.js'

const ID_PATTERN = /^[A-Za-z0-9-]+$/

function validId(value) {
  return typeof value === 'string' && ID_PATTERN.test(value)
}

/**
 * Submit styled form to HubSpot Forms API (no Formspree).
 * Docs: https://developers.hubspot.com/docs/api-reference/legacy/forms-v3-legacy/guide
 */
export function bindLeadForm(form) {
  if (!form) return

  const portalId = validId(import.meta.env.VITE_HUBSPOT_PORTAL_ID)
    ? import.meta.env.VITE_HUBSPOT_PORTAL_ID
    : ''
  const formId = validId(import.meta.env.VITE_HUBSPOT_FORM_ID)
    ? import.meta.env.VITE_HUBSPOT_FORM_ID
    : ''

  const status = form.querySelector('.form-status')
  const ok = form.querySelector('.form-confirmation')
  const err = form.querySelector('.form-error')
  const button = form.querySelector('.btn-submit')

  function showError(message) {
    if (ok) ok.hidden = true
    if (err) {
      err.hidden = false
      err.textContent = message
    }
    if (status) status.hidden = false
  }

  function showOk() {
    if (err) err.hidden = true
    if (ok) ok.hidden = false
    if (status) status.hidden = false
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault()

    const gotcha = form.querySelector('[name="_gotcha"]')
    if (gotcha && gotcha.value) {
      showOk()
      form.reset()
      return
    }

    if (!form.reportValidity()) return

    if (!portalId || !formId) {
      showError(
        `El formulario aún no está conectado a HubSpot. Escríbanos a ${CONTACT_EMAIL} o configure VITE_HUBSPOT_PORTAL_ID y VITE_HUBSPOT_FORM_ID.`
      )
      return
    }

    const original = button ? button.textContent : ''
    if (button) {
      button.disabled = true
      button.textContent = 'Enviando…'
    }

    try {
      const fd = new FormData(form)
      fd.delete('_gotcha')

      const fields = [
        { name: 'firstname', value: String(fd.get('nombre') || '') },
        { name: 'email', value: String(fd.get('correo') || '') },
        { name: 'phone', value: String(fd.get('telefono') || '') },
        { name: 'whatsapp', value: String(fd.get('telefono') || '') },
        { name: 'rol_lexiatek', value: String(fd.get('rol') || '') },
        { name: 'resumen_consulta', value: String(fd.get('mensaje') || '') },
        {
          name: 'consentimiento_datos',
          value: fd.get('consentimiento') ? 'true' : 'false'
        },
        { name: 'fuente', value: 'form_landing' }
      ]

      const response = await fetch(
        `https://api.hsforms.com/submissions/v3/integration/submit/${portalId}/${formId}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            fields,
            context: {
              pageUri: window.location.href,
              pageName: document.title
            }
          })
        }
      )

      if (!response.ok) {
        throw new Error('send_failed')
      }

      showOk()
      form.reset()
    } catch {
      showError(
        `No pudimos enviar la solicitud ahora. Intente de nuevo o escriba a ${CONTACT_EMAIL}.`
      )
    } finally {
      if (button) {
        button.disabled = false
        button.textContent = original
      }
    }
  })
}
