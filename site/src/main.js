import './style.css'
import { bindLeadForm } from './forms/lead-form.js'

function initNav() {
  const toggle = document.querySelector('.nav-toggle')
  const mobile = document.getElementById('menu-movil')
  if (!toggle || !mobile) return

  toggle.addEventListener('click', () => {
    const open = toggle.getAttribute('aria-expanded') === 'true'
    toggle.setAttribute('aria-expanded', String(!open))
    toggle.setAttribute('aria-label', open ? 'Abrir menú' : 'Cerrar menú')
    if (open) mobile.setAttribute('hidden', '')
    else mobile.removeAttribute('hidden')
  })

  mobile.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      toggle.setAttribute('aria-expanded', 'false')
      toggle.setAttribute('aria-label', 'Abrir menú')
      mobile.setAttribute('hidden', '')
    })
  })
}

function initYear() {
  const year = document.getElementById('year')
  if (year) year.textContent = String(new Date().getFullYear())
}

function initReveal() {
  const targets = document.querySelectorAll(
    '.step, .legal-card, .pain-list li, .faq-item, .pricing-panel'
  )
  if (
    !('IntersectionObserver' in window) ||
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  ) {
    return
  }

  targets.forEach((el) => el.classList.add('reveal'))
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible')
          observer.unobserve(entry.target)
        }
      })
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  )
  targets.forEach((el) => observer.observe(el))
}

document.addEventListener('DOMContentLoaded', () => {
  initNav()
  initYear()
  initReveal()
  bindLeadForm(document.querySelector('.contact-form'))
})
