from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "aplus-agent-api"
    app_version: str = "0.1.0"

    database_url: str = "postgresql+asyncpg://postgres:password@127.0.0.1:5432/aplus_agent"
    redis_url: str = "redis://localhost:6379/0"

    s3_endpoint_url: str = "http://127.0.0.1:9000"
    s3_public_base_url: str | None = None
    s3_access_key: str = "rustfsadmin"
    s3_secret_key: SecretStr = SecretStr("rustfsadmin")
    s3_region: str = "us-east-1"
    s3_bucket: str = "aplus-agent"

    embedding_provider: str = "mock"
    embedding_model: str = "mock-hash-v1"
    embedding_dimensions: int = 8

    llm_provider: str = "mock"
    llm_model: str = "mock-a-plus-v1"

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )

    model_config = SettingsConfigDict(env_file=("backend/.env", ".env"), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
