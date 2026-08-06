"""Cliente HubSpot CRM v3 (Private App) + dry-run en memoria."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import httpx

from src.config import get_settings

BASE = "https://api.hubapi.com"

_dry_contacts: dict[str, dict[str, Any]] = {}
_dry_deals: list[dict[str, Any]] = []


class HubSpotError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    settings = get_settings()
    if not settings.hubspot_access_token and not settings.hubspot_dry_run:
        raise HubSpotError("Falta HUBSPOT_ACCESS_TOKEN")
    return {
        "Authorization": f"Bearer {settings.hubspot_access_token}",
        "Content-Type": "application/json",
    }


async def search_contact_by_email(email: str) -> dict[str, Any] | None:
    settings = get_settings()
    email_n = email.strip().lower()
    if settings.hubspot_dry_run:
        for c in _dry_contacts.values():
            if (c.get("properties") or {}).get("email", "").lower() == email_n:
                return c
        return None

    payload = {
        "filterGroups": [
            {
                "filters": [
                    {"propertyName": "email", "operator": "EQ", "value": email_n},
                ]
            }
        ],
        "properties": [
            "email",
            "firstname",
            "phone",
            "whatsapp",
            "tipo_cliente",
            "rol_lexiatek",
            "resumen_consulta",
            "fuente",
        ],
        "limit": 1,
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{BASE}/crm/v3/objects/contacts/search",
            headers=_headers(),
            json=payload,
        )
        if r.status_code >= 400:
            raise HubSpotError(f"search contact: {r.status_code} {r.text[:300]}")
        results = r.json().get("results") or []
        return results[0] if results else None


async def create_or_update_contact(properties: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    email = (properties.get("email") or "").strip().lower()
    if not email and not properties.get("phone") and not properties.get("whatsapp"):
        raise HubSpotError("Se requiere email o WhatsApp/teléfono")

    existing = await search_contact_by_email(email) if email else None

    if settings.hubspot_dry_run:
        if existing:
            existing["properties"].update(properties)
            existing["properties"]["email"] = email or existing["properties"].get("email")
            return existing
        cid = str(uuid4())
        contact = {"id": cid, "properties": {**properties, "email": email}}
        _dry_contacts[cid] = contact
        return contact

    async with httpx.AsyncClient(timeout=30.0) as client:
        if existing:
            cid = existing["id"]
            r = await client.patch(
                f"{BASE}/crm/v3/objects/contacts/{cid}",
                headers=_headers(),
                json={"properties": properties},
            )
        else:
            r = await client.post(
                f"{BASE}/crm/v3/objects/contacts",
                headers=_headers(),
                json={"properties": properties},
            )
        if r.status_code >= 400:
            raise HubSpotError(f"upsert contact: {r.status_code} {r.text[:400]}")
        return r.json()


async def create_deal_for_contact(
    *,
    contact_id: str,
    dealname: str,
    resumen: str,
) -> dict[str, Any]:
    settings = get_settings()
    props = {
        "dealname": dealname,
        "pipeline": settings.hubspot_deal_pipeline,
        "dealstage": settings.hubspot_deal_stage,
        "description": resumen[:1000],
    }

    if settings.hubspot_dry_run:
        deal = {"id": str(uuid4()), "properties": props, "contact_id": contact_id}
        _dry_deals.append(deal)
        return deal

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{BASE}/crm/v3/objects/deals",
            headers=_headers(),
            json={
                "properties": props,
                "associations": [
                    {
                        "to": {"id": contact_id},
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 3,
                            }
                        ],
                    }
                ],
            },
        )
        if r.status_code >= 400:
            # Fallback: create deal then associate
            r2 = await client.post(
                f"{BASE}/crm/v3/objects/deals",
                headers=_headers(),
                json={"properties": props},
            )
            if r2.status_code >= 400:
                raise HubSpotError(f"create deal: {r2.status_code} {r2.text[:400]}")
            deal = r2.json()
            await client.put(
                f"{BASE}/crm/v4/objects/deals/{deal['id']}/associations/contacts/{contact_id}/deal_to_contact",
                headers=_headers(),
            )
            return deal
        return r.json()


async def add_note_to_contact(*, contact_id: str, body: str) -> dict[str, Any]:
    settings = get_settings()
    if settings.hubspot_dry_run:
        return {"id": str(uuid4()), "body": body, "contact_id": contact_id}

    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(
            f"{BASE}/crm/v3/objects/notes",
            headers=_headers(),
            json={
                "properties": {
                    "hs_note_body": body,
                    "hs_timestamp": str(int(__import__("time").time() * 1000)),
                },
                "associations": [
                    {
                        "to": {"id": contact_id},
                        "types": [
                            {
                                "associationCategory": "HUBSPOT_DEFINED",
                                "associationTypeId": 202,
                            }
                        ],
                    }
                ],
            },
        )
        if r.status_code >= 400:
            raise HubSpotError(f"create note: {r.status_code} {r.text[:400]}")
        return r.json()


def dry_run_snapshot() -> dict[str, Any]:
    return {
        "contacts": list(_dry_contacts.values()),
        "deals": list(_dry_deals),
    }
