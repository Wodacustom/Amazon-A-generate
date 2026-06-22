"""模型调用通用类型。"""

from collections.abc import Sequence
from typing import Protocol

from app.services.model_config import ModelProfileConfig

Message = dict[str, str]


class ModelClient(Protocol):
    """统一模型客户端接口。"""

    profile: ModelProfileConfig

    async def chat_text(self, messages: Sequence[Message], *, temperature: float | None = None) -> str:
        """执行聊天模型请求。"""

    async def embed_query(self, text: str) -> list[float]:
        """执行单条 embedding 请求。"""

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """执行批量 embedding 请求。"""
