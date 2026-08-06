from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    hubspot_access_token: str = ""
    hubspot_dry_run: bool = True
    hubspot_deal_pipeline: str = "default"
    hubspot_deal_stage: str = "appointmentscheduled"

    usd_to_cop: float = 4100.0
    agent_max_total_tokens: int = 30000

    port: int = 8787
    cors_origins: str = (
        "http://localhost:5195,http://127.0.0.1:5195,"
        "https://rdebiasec.github.io,https://lexiatek.com"
    )
    notify_email: str = "ricardo.debiase@dbx-solutions.com"
    usage_admin_token: str = "cambia-este-secreto"
    usage_store_path: str = "./data/usage.jsonl"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
