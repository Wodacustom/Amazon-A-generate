"""应用配置。

配置优先从环境变量读取，本地可使用 backend/.env 或根目录 .env。
"""

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """后端运行所需的环境配置。"""

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

    jwt_secret_key: SecretStr = SecretStr("dev-secret-change-me")
    jwt_expire_minutes: int = 1440
    model_config_secret_key: SecretStr | None = None
    admin_username: str = "admin"
    admin_password: SecretStr = SecretStr("admin123456")

    embedding_dimensions: int = 1536

    allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ]
    )

    # extra="ignore" 允许旧环境变量存在，便于重构期平滑过渡。
    model_config = SettingsConfigDict(env_file=("backend/.env", ".env"), env_file_encoding="utf-8", extra="ignore")


settings = Settings()
