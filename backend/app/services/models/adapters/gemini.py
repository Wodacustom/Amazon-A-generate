"""Gemini 模型适配器占位。"""

from collections.abc import Sequence

from app.services.model_config import ModelConfigurationError, ModelProfileConfig
from app.services.models.types import Message


class GeminiAdapter:
    """Gemini 适配器。

    当前项目未引入 Gemini SDK；保留 adapter 边界，配置到该 provider 时给出明确错误。
    """

    provider_name = "gemini"

    def __init__(self, profile: ModelProfileConfig) -> None:
        self.profile = profile

    async def chat_text(self, messages: Sequence[Message], *, temperature: float | None = None) -> str:
        raise ModelConfigurationError("GeminiAdapter requires a Gemini SDK integration before use.")

    async def embed_query(self, text: str) -> list[float]:
        raise ModelConfigurationError("GeminiAdapter embedding is not implemented.")

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        raise ModelConfigurationError("GeminiAdapter embedding is not implemented.")
