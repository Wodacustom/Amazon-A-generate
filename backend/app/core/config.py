from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "aplus-agent-api"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+asyncpg://postgres:password@127.0.0.1:5432/aplus_agent"
    redis_url: str = "redis://localhost:6379/0"
    storage_backend: str = "local"
    local_storage_dir: str = "./storage"
    scene_agent_provider: str = "rule"
    product_info_agent_provider: str = "rule"
    generation_agent_provider: str = "mock"
    image_generation_provider: str = "mock"
    default_image_model: str = "nanobanana_pro"
    dashscope_api_key: SecretStr | None = None
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    dashscope_model: str = "qwen3.6-plus"
    dashscope_timeout_seconds: float = 20.0
    gemini_api_key: SecretStr | None = None
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"
    gemini_model: str = "gemini-3.1-pro"
    gemini_image_model: str = "gemini-3-pro-image"
    gemini_timeout_seconds: float = 30.0
    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
            "http://localhost:5175",
            "http://127.0.0.1:5175",
            "http://localhost:5176",
            "http://127.0.0.1:5176",
        ]
    )

    model_config = SettingsConfigDict(env_file=("backend/.env", ".env"), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
