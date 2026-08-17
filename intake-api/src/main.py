"""API FastAPI — widget intake LexiaTek + gates WhatsApp."""

from __future__ import annotations

import re
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from src.agent import run_intake_turn
from src.config import get_settings, validate_settings_or_raise
from src.hubspot_client import dry_run_snapshot
from src.rate_limit import chat_limiter
from src.usage_store import summarize_usage
from src.whatsapp_webhook import router as whatsapp_router

# Solo UUIDs (evita conversation_id arbitrarios / sondeo).
_UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        response.headers.setdefault("Cache-Control", "no-store")
        return response


@asynccontextmanager
async def lifespan(_app: FastAPI):
    validate_settings_or_raise()
    yield


app = FastAPI(title="LexiaTek Intake API", version="0.3.0", lifespan=lifespan)
settings = get_settings()

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Hub-Signature-256"],
)
app.include_router(whatsapp_router)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    consent: bool = False


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    crm_written: bool = False
    usage: dict
    estimated_cost_usd: float | None = None
    estimated_cost_cop: float | None = None
    offline: bool = False


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for") or ""
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _resolve_conversation_id(raw: str | None) -> str:
    cid = (raw or "").strip()
    if not cid:
        return str(uuid4())
    if not _UUID_RE.match(cid):
        raise HTTPException(status_code=400, detail="conversation_id inválido")
    return cid


@app.get("/health")
async def health():
    return {"ok": True, "service": "lexiatek-intake-api", "version": "0.3.0"}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    s = get_settings()
    ip = _client_ip(request)
    ok, reason = chat_limiter.allow(
        ip,
        per_minute=s.chat_rate_limit_per_minute,
        per_day=s.chat_rate_limit_per_day,
    )
    if not ok:
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes. Intente más tarde o use el formulario de contacto.",
            headers={"Retry-After": "60" if reason == "rate_limit_minute" else "3600"},
        )

    conversation_id = _resolve_conversation_id(req.conversation_id)

    result = await run_intake_turn(
        conversation_id=conversation_id,
        message=req.message.strip(),
        consent=req.consent,
    )
    return ChatResponse(
        conversation_id=conversation_id,
        reply=result["reply"],
        crm_written=bool(result.get("crm_written")),
        usage=result.get("usage") or {},
        estimated_cost_usd=result.get("estimated_cost_usd"),
        estimated_cost_cop=result.get("estimated_cost_cop"),
        offline=bool(result.get("offline")),
    )


def _check_admin(authorization: str | None) -> None:
    expected = (get_settings().usage_admin_token or "").strip()
    bearer = ""
    if authorization and authorization.lower().startswith("bearer "):
        bearer = authorization[7:].strip()
    if not expected or not bearer or bearer != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/v1/usage")
async def usage(
    days: int = Query(default=7, ge=1, le=90),
    authorization: str | None = Header(default=None),
):
    _check_admin(authorization)
    return summarize_usage(get_settings().usage_store_path, days=days)


@app.get("/v1/debug/dry-run")
async def debug_dry_run(authorization: str | None = Header(default=None)):
    """Solo útil con HUBSPOT_DRY_RUN=true."""
    _check_admin(authorization)
    if not get_settings().hubspot_dry_run:
        raise HTTPException(status_code=400, detail="Dry-run desactivado")
    return dry_run_snapshot()
