import { CONTACT_EMAIL } from '../legal/constants.js'

const FORMSPREE_ID_PATTERN = /^[A-Za-z0-9]+$/

function isValidFormspreeId(formId) {
  return typeof formId === 'string' && FORMSPREE_ID_PATTERN.test(formId)
}

export function bindLeadForm(form) {
  if (!form) return

  const rawFormId = import.meta.env.VITE_FORMSPREE_FORM_ID
  const formId = isValidFormspreeId(rawFormId) ? rawFormId : ''
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

    if (!formId) {
      showError(
        `El formulario aún no está conectado. Escríbanos a ${CONTACT_EMAIL} o configure VITE_FORMSPREE_FORM_ID en desarrollo.`
      )
      return
    }

    const original = button ? button.textContent : ''
    if (button) {
      button.disabled = true
      button.textContent = 'Enviando…'
    }

    try {
      const body = new FormData(form)
      body.delete('_gotcha')
      const response = await fetch(`https://formspree.io/f/${formId}`, {
        method: 'POST',
        body,
        headers: { Accept: 'application/json' }
      })

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
