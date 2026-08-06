/**
 * Widget conversacional de intake LexiaTek → intake-api (Agents SDK + HubSpot).
 */
const DEFAULT_API =
  import.meta.env.VITE_INTAKE_API_URL?.replace(/\/$/, '') || 'http://127.0.0.1:8787'

const LEGAL_NOTE =
  'Respuesta orientativa. No constituye asesoría jurídica hasta la revisión de un abogado de LexiaTek.'

function el(tag, attrs = {}, children = []) {
  const node = document.createElement(tag)
  Object.entries(attrs).forEach(([k, v]) => {
    if (k === 'className') node.className = v
    else if (k === 'text') node.textContent = v
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2).toLowerCase(), v)
    else if (v === false || v == null) return
    else node.setAttribute(k, v === true ? '' : String(v))
  })
  children.forEach((c) => {
    if (c == null) return
    node.appendChild(typeof c === 'string' ? document.createTextNode(c) : c)
  })
  return node
}

export function bindIntakeWidget(root = document.body) {
  if (document.getElementById('lex-intake-root')) return

  let conversationId = sessionStorage.getItem('lex_intake_cid') || ''
  let open = false
  let consent = sessionStorage.getItem('lex_intake_consent') === '1'
  let busy = false

  const launcher = el('button', {
    type: 'button',
    className: 'lex-intake-launcher',
    'aria-label': 'Abrir chat de asesoría LexiaTek',
    text: 'Chat asesoría',
  })

  const panel = el('div', {
    className: 'lex-intake-panel',
    hidden: true,
    role: 'dialog',
    'aria-label': 'Chat de asesoría inicial LexiaTek',
  })

  const header = el('div', { className: 'lex-intake-header' }, [
    el('div', {}, [
      el('strong', { text: 'LexiaTek' }),
      el('p', { className: 'lex-intake-sub', text: 'Intake · abogado humano revisa' }),
    ]),
    el('button', {
      type: 'button',
      className: 'lex-intake-close',
      'aria-label': 'Cerrar chat',
      text: '×',
      onClick: () => setOpen(false),
    }),
  ])

  const messages = el('div', {
    className: 'lex-intake-messages',
    'aria-live': 'polite',
  })

  const consentSpan = el('span', {})
  consentSpan.append(
    document.createTextNode('Autorizo el '),
    el('a', { href: 'tratamiento-datos.html', target: '_blank', rel: 'noopener', text: 'tratamiento de mis datos' }),
    document.createTextNode(' (Ley 1581) para contactarme ('),
    el('a', { href: 'privacidad.html', target: '_blank', rel: 'noopener', text: 'privacidad' }),
    document.createTextNode(').')
  )
  const consentBox = el('label', { className: 'lex-intake-consent' }, [
    el('input', {
      type: 'checkbox',
      id: 'lex-intake-consent',
      checked: consent || undefined,
      onChange: (e) => {
        consent = e.target.checked
        sessionStorage.setItem('lex_intake_consent', consent ? '1' : '0')
      },
    }),
    consentSpan,
  ])

  const form = el('form', { className: 'lex-intake-form' })
  const input = el('textarea', {
    className: 'lex-intake-input',
    rows: '2',
    placeholder: 'Cuéntenos su situación…',
    maxlength: '3500',
    'aria-label': 'Mensaje',
  })
  const send = el('button', {
    type: 'submit',
    className: 'lex-intake-send',
    text: 'Enviar',
  })
  form.append(input, send)

  const note = el('p', { className: 'lex-intake-note', text: LEGAL_NOTE })

  panel.append(header, messages, consentBox, form, note)
  const wrap = el('div', { id: 'lex-intake-root', className: 'lex-intake-root' }, [
    panel,
    launcher,
  ])
  root.appendChild(wrap)

  function setOpen(next) {
    open = next
    if (open) {
      panel.removeAttribute('hidden')
      launcher.setAttribute('aria-expanded', 'true')
      if (!messages.childElementCount) {
        pushBot(
          'Hola. Soy el asistente de intake de LexiaTek. Puedo ayudarle a dejar sus datos para una asesoría penal inicial. Un abogado humano revisará. ¿Es usted víctima, investigado o familiar?'
        )
      }
      input.focus()
    } else {
      panel.setAttribute('hidden', '')
      launcher.setAttribute('aria-expanded', 'false')
    }
  }

  launcher.addEventListener('click', () => setOpen(!open))

  function pushBot(text) {
    messages.appendChild(el('div', { className: 'lex-intake-bubble bot', text }))
    messages.scrollTop = messages.scrollHeight
  }

  function pushUser(text) {
    messages.appendChild(el('div', { className: 'lex-intake-bubble user', text }))
    messages.scrollTop = messages.scrollHeight
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault()
    const text = input.value.trim()
    if (!text || busy) return
    if (!consent) {
      pushBot('Marque el consentimiento de tratamiento de datos para continuar.')
      return
    }
    busy = true
    send.disabled = true
    pushUser(text)
    input.value = ''
    try {
      const res = await fetch(`${DEFAULT_API}/v1/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          conversation_id: conversationId || null,
          consent: true,
        }),
      })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const data = await res.json()
      conversationId = data.conversation_id
      sessionStorage.setItem('lex_intake_cid', conversationId)
      pushBot(data.reply || 'Gracias. Un abogado le contactará.')
      if (data.crm_written) {
        pushBot('Registro recibido. LexiaTek le contactará pronto por WhatsApp o correo.')
      }
    } catch {
      pushBot(
        'No pudimos conectar el chat ahora. Use el formulario de esta página o escriba a contacto@lexiatek.com.'
      )
    } finally {
      busy = false
      send.disabled = false
      input.focus()
    }
  })
}
