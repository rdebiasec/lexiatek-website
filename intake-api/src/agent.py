"""Agente de intake LexiaTek (OpenAI Agents SDK) → HubSpot."""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from agents import Agent, Runner, function_tool

from src.config import get_settings
from src import hubspot_client as hs
from src.pricing import estimate_cost_cop, estimate_cost_usd
from src.sessions import sessions
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
NUNCA pidas evidencias, documentos, chats, audios ni pruebas por este canal.
Si el usuario intenta enviar pruebas, indícale que un abogado le indicará un canal seguro.
Minimiza lo que guardas: resumen corto, sin narrativa procesal detallada.
"""


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
        resumen: Resumen breve de la consulta (sin pruebas ni detalle íntimo).
        email: Correo (recomendado).
        whatsapp: Celular/WhatsApp.
        consentimiento: Debe ser True; el widget ya lo capturó.
    """
    settings = get_settings()
    if not consentimiento:
        return json.dumps({"ok": False, "error": "Sin consentimiento no se escribe en CRM"})
    if not email and not whatsapp:
        return json.dumps({"ok": False, "error": "Falta email o WhatsApp"})

    first = (nombre or "").strip().split(" ", 1)[0]
    resumen_safe = resumen.strip()[: settings.hubspot_resumen_max_chars]
    props = {
        "firstname": first or nombre,
        "lastname": (nombre.strip()[len(first) :].strip() if nombre else "") or "-",
        "email": (email or "").strip().lower(),
        "phone": (whatsapp or "").strip(),
        "whatsapp": (whatsapp or "").strip(),
        "tipo_cliente": tipo_cliente.strip().lower(),
        "rol_lexiatek": rol.strip().lower(),
        "resumen_consulta": resumen_safe,
        "consentimiento_datos": "true",
        "fuente": "widget_agente",
    }
    contact = await hs.create_or_update_contact({k: v for k, v in props.items() if v})
    contact_id = str(contact.get("id"))
    deal = await hs.create_deal_for_contact(
        contact_id=contact_id,
        dealname=f"Asesoría inicial — {nombre.strip()[:60]}",
        resumen=resumen_safe,
    )
    note_body = (
        f"Lead widget LexiaTek\nRol: {rol}\nTipo: {tipo_cliente}\n"
        f"WA: {whatsapp}\nEmail: {email}\n\n{resumen_safe}"
    )[: settings.hubspot_note_max_chars]
    await hs.add_note_to_contact(contact_id=contact_id, body=note_body)
    return json.dumps(
        {
            "ok": True,
            "contact_id": contact_id,
            "deal_id": deal.get("id"),
            "dry_run": settings.hubspot_dry_run,
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
    empty_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    if not consent:
        return {
            "reply": (
                "Para continuar necesitamos su autorización de tratamiento de datos "
                "(Ley 1581). Márquela en el widget e intente de nuevo."
            ),
            "crm_written": False,
            "usage": empty_usage,
        }

    already = sessions.total_tokens(conversation_id)
    if settings.agent_max_total_tokens > 0 and already >= settings.agent_max_total_tokens:
        return {
            "reply": (
                "Se alcanzó el límite de esta conversación. "
                "Por favor use el formulario de contacto o escriba a contacto@lexiatek.com."
            ),
            "crm_written": False,
            "usage": empty_usage,
            "budget_exhausted": True,
        }

    sessions.append(
        conversation_id,
        role="user",
        content=message,
        max_sessions=settings.session_max_conversations,
        ttl_seconds=settings.session_ttl_seconds,
        max_turns=settings.session_max_turns,
    )
    history = sessions.get_messages(conversation_id)

    if not settings.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
        reply = (
            "Modo local sin OPENAI_API_KEY: describa rol, resumen, nombre y WhatsApp/email. "
            "Cuando configure la API key, el agente creará el lead en HubSpot."
        )
        sessions.append(
            conversation_id,
            role="assistant",
            content=reply,
            max_sessions=settings.session_max_conversations,
            ttl_seconds=settings.session_ttl_seconds,
            max_turns=settings.session_max_turns,
        )
        return {
            "reply": reply,
            "crm_written": False,
            "usage": empty_usage,
            "offline": True,
        }

    os.environ.setdefault("OPENAI_API_KEY", settings.openai_api_key)
    agent = _build_agent()
    prompt_parts = []
    for turn in history[-12:]:
        prompt_parts.append(f"{turn['role'].upper()}: {turn['content']}")
    prompt = "\n".join(prompt_parts)

    try:
        result = await asyncio.wait_for(
            Runner.run(agent, prompt),
            timeout=settings.openai_timeout_seconds,
        )
    except asyncio.TimeoutError:
        reply = (
            "El asistente tardó demasiado en responder. "
            "Intente de nuevo o use el formulario de contacto."
        )
        sessions.append(
            conversation_id,
            role="assistant",
            content=reply,
            max_sessions=settings.session_max_conversations,
            ttl_seconds=settings.session_ttl_seconds,
            max_turns=settings.session_max_turns,
        )
        return {
            "reply": reply,
            "crm_written": False,
            "usage": empty_usage,
            "timeout": True,
        }

    usage = _usage_dict(getattr(getattr(result, "context_wrapper", None), "usage", None))
    reply = str(result.final_output or "").strip() or "Gracias. Un abogado de LexiaTek le contactará."

    sessions.add_tokens(conversation_id, usage["total_tokens"])
    sessions.append(
        conversation_id,
        role="assistant",
        content=reply,
        max_sessions=settings.session_max_conversations,
        ttl_seconds=settings.session_ttl_seconds,
        max_turns=settings.session_max_turns,
    )

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

    crm_written = False
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
