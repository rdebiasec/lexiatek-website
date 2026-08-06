/**
 * WhatsApp CTA — inactive until VITE_WHATSAPP_URL or constants.WHATSAPP_URL is set.
 */
import { WHATSAPP_URL } from './legal/constants.js'

export function bindWhatsAppCtas(root = document) {
  const url = (import.meta.env.VITE_WHATSAPP_URL || WHATSAPP_URL || '').trim()
  root.querySelectorAll('[data-whatsapp-cta]').forEach((node) => {
    if (url && /^https?:\/\//i.test(url)) {
      node.setAttribute('href', url)
      node.removeAttribute('aria-disabled')
      node.classList.remove('is-disabled')
      if (node.tagName === 'A') node.setAttribute('target', '_blank')
      node.setAttribute('rel', 'noopener noreferrer')
    } else {
      node.setAttribute('href', '#contacto')
      node.setAttribute('aria-disabled', 'true')
      node.classList.add('is-disabled')
      node.addEventListener('click', (e) => {
        // Placeholder: scroll to contact until number is configured
        if (node.getAttribute('href') === '#contacto') return
        e.preventDefault()
      })
      const label = node.getAttribute('data-wa-pending-label')
      if (label) node.textContent = label
    }
  })
}
