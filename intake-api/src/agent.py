"""Agente de intake LexiaTek (OpenAI Agents SDK) → HubSpot."""

from __future__ import annotations

import json
import os
from typing import Any

from agents import Agent, Runner, function_tool

from src.config import get_settings
from src import hubspot_client as hs
from src.pricing import estimate_cost_cop, estimate_cost_usd
from src.usage_store import append_usage

SYSTEM = """Eres el asistente de intake de Firma1 de Abogados LexiaTek (Colombia).
Habla español claro (es-CO). NO das consejo jurídico ni garantizas resultados judiciales.
Tu trabajo: calificar si es un lead pertinente de asesoría penal inicial y, con consentimiento,
crear/actualizar el contacto en HubSpot.

Flujo sugerido:
1) Saludo breve + explicar que un abogado humano revisará.
2) Preguntar rol: víctima / investigado / familiar / otro.
3) Resumen breve (sin detalles íntimos innecesarios).
4) Natural o jurídica.
5) Nombre + WhatsApp y/o email.
6) Confirmar que YA autorizó tratamiento de datos (el widget lo exige antes).
7) Si hay canal de contacto + resumen + rol → llama create_lead_in_hubspot.
8) Confirma: “Un abogado de LexiaTek le contactará pronto.”

Si solo pregunta genérica de FAQ → responde corto y NO crees CRM.
Si pide estrategia procesal / “¿gano el caso?” → rehúsa y ofrece dejar datos para abogado.
Nunca inventes honorarios fijos ni porcentajes de éxito.
"""

_sessions: dict[str, list[dict[str, str]]] = {}


def _usage_dict(usage: Any) -> dict[str, int]:
    if usage is None:
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    return {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
    }


@function_tool
async def create_lead_in_hubspot(
    nombre: str,
    rol: str,
    tipo_cliente: str,
    resumen: str,
    email: str = "",
    whatsapp: str = "",
    consentimiento: bool = True,
) -> str:
    """Crea o actualiza Contact + Deal Asesoría inicial + nota en HubSpot.

    Args:
        nombre: Nombre completo del lead.
        rol: victima | investigado | familiar | otro
        tipo_cliente: natural | juridica
        resumen: Resumen breve de la consulta.
        email: Correo (recomendado).
        whatsapp: Celular/WhatsApp.
        consentimiento: Debe ser True; el widget ya lo capturó.
    """
    if not consentimiento:
        return json.dumps({"ok": False, "error": "Sin consentimiento no se escribe en CRM"})
    if not email and not whatsapp:
        return json.dumps({"ok": False, "error": "Falta email o WhatsApp"})

    first = (nombre or "").strip().split(" ", 1)[0]
    props = {
        "firstname": first or nombre,
        "lastname": (nombre.strip()[len(first) :].strip() if nombre else "") or "-",
        "email": (email or "").strip().lower(),
        "phone": (whatsapp or "").strip(),
        "whatsapp": (whatsapp or "").strip(),
        "tipo_cliente": tipo_cliente.strip().lower(),
        "rol_lexiatek": rol.strip().lower(),
        "resumen_consulta": resumen.strip()[:4000],
        "consentimiento_datos": "true",
        "fuente": "widget_agente",
    }
    # HubSpot may reject unknown custom props if not created yet — still attempt
    contact = await hs.create_or_update_contact({k: v for k, v in props.items() if v})
    contact_id = str(contact.get("id"))
    deal = await hs.create_deal_for_contact(
        contact_id=contact_id,
        dealname=f"Asesoría inicial — {nombre.strip()[:60]}",
        resumen=resumen.strip(),
    )
    await hs.add_note_to_contact(
        contact_id=contact_id,
        body=(
            f"Lead widget LexiaTek\nRol: {rol}\nTipo: {tipo_cliente}\n"
            f"WA: {whatsapp}\nEmail: {email}\n\n{resumen}"
        ),
    )
    return json.dumps(
        {
            "ok": True,
            "contact_id": contact_id,
            "deal_id": deal.get("id"),
            "dry_run": get_settings().hubspot_dry_run,
            "notify": get_settings().notify_email,
        },
        ensure_ascii=False,
    )


def _build_agent() -> Agent:
    return Agent(
        name="LexiaTek Intake",
        instructions=SYSTEM,
        model=get_settings().openai_model,
        tools=[create_lead_in_hubspot],
    )


async def run_intake_turn(
    *,
    conversation_id: str,
    message: str,
    consent: bool,
) -> dict[str, Any]:
    settings = get_settings()
    if not consent:
        return {
            "reply": (
                "Para continuar necesitamos su autorización de tratamiento de datos "
                "(Ley 1581). Márquela en el widget e intente de nuevo."
            ),
            "crm_written": False,
            "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        }

    history = _sessions.setdefault(conversation_id, [])
    history.append({"role": "user", "content": message})

    if not settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
        # Offline stub for smoke without OpenAI
        reply = (
            "Modo local sin OPENAI_API_KEY: describa rol, resumen, nombre y WhatsApp/email. "
            "Cuando configure la API key, el agente creará el lead en HubSpot."
        )
        history.append({"role": "assistant", "content": reply})
        return {
            "reply": reply,
            "crm_written": False,
            "usage": {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            "offline": True,
        }

    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    agent = _build_agent()
    # Compact history for the runner
    prompt_parts = []
    for turn in history[-12:]:
        prompt_parts.append(f"{turn['role'].upper()}: {turn['content']}")
    prompt = "\n".join(prompt_parts)

    result = await Runner.run(agent, prompt)
    usage = _usage_dict(getattr(getattr(result, "context_wrapper", None), "usage", None))
    reply = str(result.final_output or "").strip() or "Gracias. Un abogado de LexiaTek le contactará."

    if settings.agent_max_total_tokens > 0 and usage["total_tokens"] > settings.agent_max_total_tokens:
        reply += (
            f"\n\n(Nota interna: este turno superó el presupuesto de "
            f"{settings.agent_max_total_tokens} tokens.)"
        )

    history.append({"role": "assistant", "content": reply})

    cost_usd = estimate_cost_usd(
        model=settings.openai_model,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
    )
    cost_cop = estimate_cost_cop(
        model=settings.openai_model,
        input_tokens=usage["input_tokens"],
        output_tokens=usage["output_tokens"],
        usd_to_cop=settings.usd_to_cop,
    )

    append_usage(
        settings.usage_store_path,
        {
            "conversation_id": conversation_id,
            "model": settings.openai_model,
            **usage,
            "estimated_cost_usd": cost_usd,
            "estimated_cost_cop": cost_cop,
            "usd_to_cop": settings.usd_to_cop,
        },
    )

    crm_written = "contact_id" in reply.lower() or any(
        "create_lead_in_hubspot" in str(getattr(i, "raw_item", i)) for i in (result.new_items or [])
    )
    # Better signal: inspect tool outputs in new_items
    for item in result.new_items or []:
        raw = getattr(item, "output", None) or getattr(item, "raw_item", None)
        text = str(raw)
        if '"ok": true' in text or '"ok":true' in text:
            crm_written = True
            break

    return {
        "reply": reply,
        "crm_written": crm_written,
        "usage": usage,
        "estimated_cost_usd": cost_usd,
        "estimated_cost_cop": cost_cop,
    }
