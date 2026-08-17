from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Defaults inseguros que deben rechazarse al arrancar (salvo ALLOW_INSECURE_DEFAULTS=true en local).
INSECURE_ADMIN_TOKENS = frozenset(
    {
        "",
        "cambia-este-secreto",
        "changeme",
        "secret",
        "admin",
        "password",
    }
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"
    openai_timeout_seconds: float = 60.0

    hubspot_access_token: str = ""
    hubspot_dry_run: bool = True
    hubspot_deal_pipeline: str = "default"
    hubspot_deal_stage: str = "appointmentscheduled"

    usd_to_cop: float = 4100.0
    # Hard stop: no se llama a OpenAI si la conversación ya acumuló este total.
    agent_max_total_tokens: int = 30000

    port: int = 8787
    cors_origins: str = (
        "http://localhost:5195,http://127.0.0.1:5195,"
        "https://rdebiasec.github.io,https://lexiatek.com"
    )
    notify_email: str = "ricardo.debiase@dbx-solutions.com"
    usage_admin_token: str = ""
    usage_store_path: str = "./data/usage.jsonl"

    # Solo para smoke local. En Render debe ser false / ausente.
    allow_insecure_defaults: bool = False

    chat_rate_limit_per_minute: int = 10
    chat_rate_limit_per_day: int = 200

    session_max_conversations: int = 500
    session_ttl_seconds: int = 3600
    session_max_turns: int = 40

    # Notas CRM: minimización (no expediente de pruebas).
    hubspot_note_max_chars: int = 800
    hubspot_resumen_max_chars: int = 500

    # WhatsApp Cloud API (fase 2 / gates de deployment final)
    whatsapp_verify_token: str = ""
    meta_app_secret: str = ""
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_settings_or_raise(settings: Settings | None = None) -> None:
    s = settings or get_settings()
    token = (s.usage_admin_token or "").strip()
    if s.allow_insecure_defaults:
        return
    if token.lower() in INSECURE_ADMIN_TOKENS or token in INSECURE_ADMIN_TOKENS:
        raise RuntimeError(
            "USAGE_ADMIN_TOKEN ausente o inseguro. Defina un secreto fuerte "
            "(o ALLOW_INSECURE_DEFAULTS=true solo en local)."
        )
