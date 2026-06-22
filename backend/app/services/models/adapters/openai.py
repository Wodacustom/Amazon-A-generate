"""OpenAI-compatible 厂商适配器。"""

from collections.abc import Sequence
from typing import Any

from app.services.model_config import ModelConfigurationError, ModelProfileConfig
from app.services.models.types import Message


class OpenAIAdapter:
    """OpenAI-compatible 模型客户端。"""

    provider_name = "openai"

    def __init__(self, profile: ModelProfileConfig) -> None:
        self.profile = profile

    async def chat_text(self, messages: Sequence[Message], *, temperature: float | None = None) -> str:
        if not self.profile.base_url:
            raise ModelConfigurationError(f"{self.profile.name} requires base_url.")
        if not self.profile.api_key:
            raise ModelConfigurationError(f"{self.profile.name} requires api_key.")
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise ModelConfigurationError("langchain-openai is required for OpenAI-compatible chat.") from exc
        model = ChatOpenAI(
            model=self.profile.model,
            api_key=self.profile.api_key,
            base_url=self.profile.base_url,
            timeout=self.profile.timeout_seconds,
            temperature=self.profile.temperature if temperature is None else temperature,
        )
        response = await model.ainvoke([(message["role"], message["content"]) for message in messages])
        return str(response.content)

    async def embed_query(self, text: str) -> list[float]:
        return list(await self._embedding_model().aembed_query(text))

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        return [list(vector) for vector in await self._embedding_model().aembed_documents(list(texts))]

    def _embedding_model(self) -> Any:
        if not self.profile.base_url:
            raise ModelConfigurationError(f"{self.profile.name} requires base_url.")
        if not self.profile.api_key:
            raise ModelConfigurationError(f"{self.profile.name} requires api_key.")
        try:
            from langchain_openai import OpenAIEmbeddings
        except ImportError as exc:
            raise ModelConfigurationError("langchain-openai is required for OpenAI-compatible embedding.") from exc
        return OpenAIEmbeddings(
            model=self.profile.model,
            api_key=self.profile.api_key,
            base_url=self.profile.base_url,
            dimensions=self.profile.dimensions,
        )


class QwenAdapter(OpenAIAdapter):
    """通义千问 OpenAI-compatible 适配器。"""

    provider_name = "qwen"


class VLLMAdapter(OpenAIAdapter):
    """vLLM OpenAI-compatible 适配器。"""

    provider_name = "vllm"


class NewAPIAdapter(OpenAIAdapter):
    """NewAPI OpenAI-compatible 适配器。"""

    provider_name = "newapi"
