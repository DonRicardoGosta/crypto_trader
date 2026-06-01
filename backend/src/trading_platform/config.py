"""Infrastructure settings (env only)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://trading:trading@localhost:5432/trading"
    kafka_bootstrap: str = "localhost:19092"
    secrets_master_key: str = "dev-master-key-change-in-production-32b"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    realtime_ws_port: int = 8001
    config_cache_ttl_seconds: float = 2.0
    event_queue_max_size: int = 10_000


settings = Settings()
