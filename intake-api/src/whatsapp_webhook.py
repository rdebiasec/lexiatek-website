"""WhatsApp Cloud API webhook — verificación + firma (gates de deployment final)."""

from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Query, Request, Response

from src.config import get_settings

logger = logging.getLogger("lexiatek.whatsapp")

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


def _verify_signature(app_secret: str, raw_body: bytes, signature_header: str | None) -> bool:
    """Meta envía X-Hub-Signature-256: sha256=<hex>."""
    if not app_secret or not signature_header:
        return False
    prefix = "sha256="
    if not signature_header.startswith(prefix):
        return False
    expected = hmac.new(app_secret.encode("utf-8"), raw_body, hashlib.sha256).hexdigest()
    received = signature_header[len(prefix) :]
    return hmac.compare_digest(expected, received)


@router.get("")
async def whatsapp_verify(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    """Handshake de suscripción Meta (GET)."""
    settings = get_settings()
    verify = (settings.whatsapp_verify_token or "").strip()
    if not verify:
        raise HTTPException(status_code=503, detail="WhatsApp verify token no configurado")
    if hub_mode == "subscribe" and hub_verify_token == verify and hub_challenge is not None:
        return Response(content=hub_challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Verificación WhatsApp rechazada")


@router.post("")
async def whatsapp_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
):
    """
    Recibe eventos WhatsApp. Requiere META_APP_SECRET y firma válida.
    No persiste el cuerpo del mensaje (minimización / no-evidencias en logs).
    """
    settings = get_settings()
    secret = (settings.meta_app_secret or "").strip()
    if not secret:
        raise HTTPException(status_code=503, detail="META_APP_SECRET no configurado")

    raw = await request.body()
    if not _verify_signature(secret, raw, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Firma X-Hub-Signature-256 inválida")

    # Parse mínimo sin loguear contenido sensible.
    try:
        payload: dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="JSON inválido") from None

    entries = payload.get("entry") if isinstance(payload, dict) else None
    n_entries = len(entries) if isinstance(entries, list) else 0
    # Solo metadatos agregados — nunca texto de mensajes ni media IDs en logs.
    logger.info("whatsapp_webhook_accepted entries=%s", n_entries)

    # Sprint A: BSP maneja inbox. Este endpoint es gate técnico listo para fase 2 agente.
    # ACK inmediato a Meta (200) para evitar reintentos.
    return {"ok": True, "accepted": n_entries}
