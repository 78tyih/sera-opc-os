from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SMI_", env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://smi:smi@localhost:5432/smi"
    ingest_api_key: str | None = None
    log_level: str = "INFO"

    # OpenAI-compatible endpoint. DeepSeek and other compatible providers can
    # be used without changing the intelligence pipeline.
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str | None = None
    report_timezone: str = "Asia/Singapore"


@lru_cache
def get_settings() -> Settings:
    return Settings()
