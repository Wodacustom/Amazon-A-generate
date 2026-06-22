"""模型调用策略。"""

import json
from collections.abc import Sequence
from typing import Any, TypeVar

from app.core.config import settings
from app.services.model_config import ModelConfigurationError, ModelProfileConfig
from app.services.models.factory import ModelClientFactory
from app.services.models.fallback import FallbackExecutor, FallbackResult
from app.services.models.types import Message

T = TypeVar("T")


class ChatJsonStrategy:
    """JSON 聊天模型调用策略。

    Strategy 只负责一次调用的执行规则：选择 client、解析 JSON、校验响应契约。
    """

    def __init__(self, factory: ModelClientFactory, fallback: FallbackExecutor) -> None:
        self.factory = factory
        self.fallback = fallback

    async def execute(
        self,
        *,
        route,
        messages: Sequence[Message],
        response_model: type[T],
        temperature: float | None = None,
    ) -> FallbackResult[tuple[T, ModelProfileConfig]]:
        """调用主/备聊天模型，并返回响应对象和实际使用的 profile。"""
        async def call(profile: ModelProfileConfig) -> tuple[T, ModelProfileConfig]:
            content = await self.factory.create(profile).chat_text(messages, temperature=temperature)
            parsed = _parse_json_object(content)
            if response_model is dict:
                return parsed, profile
            return response_model.model_validate(parsed), profile

        return await self.fallback.run(
            lambda: call(route.primary),
            (lambda: call(route.fallback)) if route.fallback else None,
        )


class EmbeddingStrategy:
    """Embedding 模型调用策略。"""

    def __init__(self, factory: ModelClientFactory, fallback: FallbackExecutor) -> None:
        self.factory = factory
        self.fallback = fallback

    async def embed_query(self, *, route, text: str) -> FallbackResult[tuple[list[float], ModelProfileConfig]]:
        """调用 embedding 模型生成单条向量。"""
        async def call(profile: ModelProfileConfig) -> tuple[list[float], ModelProfileConfig]:
            self._validate_dimensions(profile)
            return await self.factory.create(profile).embed_query(text), profile

        return await self.fallback.run(
            lambda: call(route.primary),
            (lambda: call(route.fallback)) if route.fallback else None,
        )

    async def embed_documents(
        self, *, route, texts: Sequence[str]
    ) -> FallbackResult[tuple[list[list[float]], ModelProfileConfig]]:
        """调用 embedding 模型批量生成向量。"""
        async def call(profile: ModelProfileConfig) -> tuple[list[list[float]], ModelProfileConfig]:
            self._validate_dimensions(profile)
            return await self.factory.create(profile).embed_documents(texts), profile

        return await self.fallback.run(
            lambda: call(route.primary),
            (lambda: call(route.fallback)) if route.fallback else None,
        )

    def _validate_dimensions(self, profile: ModelProfileConfig) -> None:
        if profile.dimensions != settings.embedding_dimensions:
            raise ModelConfigurationError(
                f"Embedding profile {profile.name} dimensions {profile.dimensions} "
                f"does not match configured vector dimensions {settings.embedding_dimensions}."
            )


def _parse_json_object(content: str) -> dict[str, Any]:
    """解析模型返回的 JSON 对象，兼容 ```json fenced 输出。"""
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    parsed = json.loads(stripped)
    if not isinstance(parsed, dict):
        raise ValueError("Model response JSON must be an object.")
    return parsed
