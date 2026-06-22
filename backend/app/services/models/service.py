"""业务统一模型调用入口。"""

from collections.abc import Sequence
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.model_config import ModelProfileConfig, ModelRouteConfig
from app.services.models.factory import ModelClientFactory
from app.services.models.fallback import FallbackExecutor
from app.services.models.registry import ModelRegistry
from app.services.models.router import ModelRouter
from app.services.models.strategy import ChatJsonStrategy, EmbeddingStrategy, ImageGenerationStrategy
from app.services.models.types import ImageGenerationInput, ImageGenerationOutput, Message

T = TypeVar("T")


class ModelService:
    """业务代码调用模型的唯一入口。

    上层业务只传业务 role 和结构化请求；本服务负责串起路由、模板渲染、
    client 创建、策略执行、fallback 和 metadata 记录。
    """

    def __init__(
        self,
        *,
        registry: ModelRegistry | None = None,
        router: ModelRouter | None = None,
        factory: ModelClientFactory | None = None,
        fallback: FallbackExecutor | None = None,
    ) -> None:
        """组装模型调用链的各层依赖，允许测试注入替身。"""
        self.registry = registry or ModelRegistry()
        self.router = router or ModelRouter(self.registry)
        self.factory = factory or ModelClientFactory()
        self.fallback = fallback or FallbackExecutor()
        self.chat_strategy = ChatJsonStrategy(self.factory, self.fallback)
        self.embedding_strategy = EmbeddingStrategy(self.factory, self.fallback)
        self.image_strategy = ImageGenerationStrategy(self.factory, self.fallback)
        self._last_metadata: dict[str, Any] = {}

    async def chat_json(
        self,
        messages: Sequence[Message] | None = None,
        *,
        db: AsyncSession | None = None,
        role: str = "a_plus_content",
        request: BaseModel | None = None,
        response_model: type[T] | None = None,
        temperature: float | None = None,
    ) -> dict[str, Any] | T:
        """按业务角色调用 JSON 聊天模型。

        如果传入 request，则先从数据库模板渲染 system/user messages；
        如果直接传 messages，则跳过模板层，主要用于测试或极少数内部调用。
        """
        route = await self.router.route(db, role, expected_type="chat")
        rendered = None
        if request is not None:
            # 模板保存在数据库，调整 prompt 或请求体后下一次调用立即生效。
            rendered = await self.registry.render_prompt(db, role, request)
            messages = rendered.messages
        if messages is None:
            raise ValueError("messages or request is required.")
        output_type: type[Any] = response_model or dict
        execution = await self.chat_strategy.execute(
            route=route,
            messages=messages,
            response_model=output_type,
            temperature=temperature,
        )
        result, profile = execution.value
        # 记录实际使用的模型和模板，便于结果落库后排查路由与 fallback 行为。
        self._last_metadata = self._metadata(role, profile, template=rendered, fallback=execution)
        return result.model_dump() if isinstance(result, BaseModel) and response_model is None else result

    async def chat_text(
        self,
        messages: Sequence[Message],
        *,
        db: AsyncSession | None = None,
        role: str = "a_plus_content",
        temperature: float | None = None,
    ) -> str:
        """按业务角色调用纯文本聊天模型。"""
        route = await self.router.route(db, role, expected_type="chat")

        async def call(profile: ModelProfileConfig) -> tuple[str, ModelProfileConfig]:
            return await self.factory.create(profile).chat_text(messages, temperature=temperature), profile

        execution = await self.fallback.run(
            lambda: call(route.primary),
            (lambda: call(route.fallback)) if route.fallback else None,
        )
        result, profile = execution.value
        self._last_metadata = self._metadata(role, profile, fallback=execution)
        return result

    async def embed_query(
        self, text: str, *, db: AsyncSession | None = None, role: str = "retrieval_embedding"
    ) -> list[float]:
        route = await self.router.route(db, role, expected_type="embedding")
        execution = await self.embedding_strategy.embed_query(route=route, text=text)
        result, profile = execution.value
        self._last_metadata = self._metadata(role, profile, fallback=execution)
        return result

    async def embed_documents(
        self, texts: Sequence[str], *, db: AsyncSession | None = None, role: str = "retrieval_embedding"
    ) -> list[list[float]]:
        route = await self.router.route(db, role, expected_type="embedding")
        execution = await self.embedding_strategy.embed_documents(route=route, texts=texts)
        result, profile = execution.value
        self._last_metadata = self._metadata(role, profile, fallback=execution)
        return result

    async def generate_image(
        self,
        request: ImageGenerationInput,
        *,
        db: AsyncSession | None = None,
        role: str = "image_generation",
        model_profile_id: int | None = None,
    ) -> ImageGenerationOutput:
        """按业务角色或指定模型档案调用图片模型。"""
        if model_profile_id is not None:
            if db is None:
                raise ValueError("db is required when model_profile_id is provided.")
            profile = await self.registry.get_profile(db, model_profile_id, expected_type="image")
            route = ModelRouteConfig(role=role, primary=profile)
        else:
            route = await self.router.route(db, role, expected_type="image")
        execution = await self.image_strategy.generate(route=route, request=request)
        result, profile = execution.value
        self._last_metadata = self._metadata(role, profile, fallback=execution)
        return result

    def llm_metadata(self) -> dict[str, Any]:
        """返回最近一次聊天模型调用的可落库摘要。"""
        return {k: v for k, v in self._last_metadata.items() if k.startswith("model_") or k.startswith("template_")}

    def embedding_metadata(self) -> dict[str, Any]:
        """返回最近一次 embedding 调用的可落库摘要。"""
        return self._last_metadata

    def image_metadata(self) -> dict[str, Any]:
        """返回最近一次图片模型调用的可落库摘要。"""
        return self._last_metadata

    def _metadata(self, role: str, profile: ModelProfileConfig, *, template=None, fallback=None) -> dict[str, Any]:
        """构建不包含密钥的模型调用 metadata。"""
        data = {
            "model_role": role,
            "model_profile": profile.name,
            "model_provider": profile.provider,
            "model_name": profile.model,
            "model_type": profile.model_type,
            "model_adapter": profile.provider,
            "model_base_url_configured": bool(profile.base_url),
            "model_fallback_used": bool(fallback.fallback_used) if fallback else False,
            "model_failure_reason": fallback.failure_reason if fallback else None,
        }
        if template is not None:
            data.update(
                {
                    "template_name": template.template_name,
                    "template_version": template.template_version,
                    "response_contract": template.response_contract,
                }
            )
        return data
