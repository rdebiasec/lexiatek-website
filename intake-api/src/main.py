"""API FastAPI — widget intake LexiaTek."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.agent import run_intake_turn
from src.config import get_settings
from src.hubspot_client import dry_run_snapshot
from src.usage_store import summarize_usage

app = FastAPI(title="LexiaTek Intake API", version="0.1.0")
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


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


@app.get("/health")
async def health():
    s = get_settings()
    return {
        "ok": True,
        "hubspot_dry_run": s.hubspot_dry_run,
        "has_hubspot_token": bool(s.hubspot_access_token),
        "has_openai": bool(s.openai_api_key),
        "notify_email": s.notify_email,
    }


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    conversation_id = (req.conversation_id or "").strip() or str(uuid4())
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


def _check_admin(authorization: str | None, token_q: str | None) -> None:
    expected = get_settings().usage_admin_token
    bearer = ""
    if authorization and authorization.lower().startswith("bearer "):
        bearer = authorization[7:].strip()
    provided = bearer or (token_q or "")
    if not expected or provided != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/v1/usage")
async def usage(
    days: int = Query(default=7, ge=1, le=90),
    authorization: str | None = Header(default=None),
    token: str | None = None,
):
    _check_admin(authorization, token)
    return summarize_usage(get_settings().usage_store_path, days=days)


@app.get("/v1/debug/dry-run")
async def debug_dry_run(
    authorization: str | None = Header(default=None),
    token: str | None = None,
):
    """Solo útil con HUBSPOT_DRY_RUN=true."""
    _check_admin(authorization, token)
    if not get_settings().hubspot_dry_run:
        raise HTTPException(status_code=400, detail="Dry-run desactivado")
    return dry_run_snapshot()
