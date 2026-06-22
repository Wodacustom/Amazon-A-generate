"""模型配置读取、模板渲染和默认配置。"""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.model_config import ModelProfile, ModelRequestTemplate, ModelRoute
from app.services.security import decrypt_secret


class ModelConfigurationError(RuntimeError):
    """模型配置不可用。"""


@dataclass(frozen=True)
class ModelProfileConfig:
    """模型档案运行时配置。"""

    name: str
    model_type: str
    provider: str
    model: str
    base_url: str | None
    api_key: str | None
    timeout_seconds: float
    temperature: float | None
    dimensions: int | None
    config: dict[str, Any]


@dataclass(frozen=True)
class ModelRouteConfig:
    """业务角色路由配置。"""

    role: str
    primary: ModelProfileConfig
    fallback: ModelProfileConfig | None = None


@dataclass(frozen=True)
class RenderedPrompt:
    """渲染后的模型消息。"""

    role: str
    template_name: str
    template_version: str
    response_contract: str
    messages: list[dict[str, str]]


class ModelConfigRepository:
    """从数据库读取模型配置；无数据库配置时回退到环境变量。

    这里是模型热配置的边界：业务调用不直接读 Settings，而是先尝试读库。
    """

    async def get_route(self, db: AsyncSession | None, role: str, *, expected_type: str) -> ModelRouteConfig:
        """获取业务 role 对应的模型路由。"""
        if db is not None:
            # 数据库配置优先，保证后台调整 route/profile 后无需重启服务。
            route = await self._get_db_route(db, role, expected_type=expected_type)
            if route is not None:
                return route
        # 没有数据库配置时使用环境变量 fallback，方便本地开发和测试。
        return self._fallback_route(role, expected_type=expected_type)

    async def get_profile(self, db: AsyncSession, profile_id: int, *, expected_type: str) -> ModelProfileConfig:
        """按 ID 获取单个模型档案，供管理测试或手动覆盖路由使用。"""
        profile = await db.get(ModelProfile, profile_id)
        if profile is None:
            raise ModelConfigurationError(f"Model profile {profile_id} not found.")
        return self._profile_config(profile, expected_type=expected_type)

    async def render_prompt(self, db: AsyncSession | None, role: str, request: BaseModel) -> RenderedPrompt:
        """从数据库模板渲染模型请求。"""
        template = await self._get_db_template(db, role) if db is not None else None
        if template is None:
            template = self._fallback_template(role)
        variables = request.variables() if hasattr(request, "variables") else {"payload": request.model_dump_json()}
        # 数据库模板只做 Python format 变量替换，不执行任何动态代码。
        return RenderedPrompt(
            role=role,
            template_name=template.name,
            template_version=template.version,
            response_contract=template.response_contract,
            messages=[
                {"role": "system", "content": template.system_prompt.format(**variables)},
                {"role": "user", "content": template.user_template.format(**variables)},
            ],
        )

    async def _get_db_route(
        self, db: AsyncSession, role: str, *, expected_type: str
    ) -> ModelRouteConfig | None:
        result = await db.execute(
            select(ModelRoute).where(ModelRoute.role == role, ModelRoute.enabled.is_(True), ModelRoute.deleted == 0)
        )
        route = result.scalar_one_or_none()
        if route is None:
            return None
        primary = await db.get(ModelProfile, route.primary_profile_id)
        fallback = await db.get(ModelProfile, route.fallback_profile_id) if route.fallback_profile_id else None
        if primary is None:
            raise ModelConfigurationError(f"Model route {role} primary profile not found.")
        return ModelRouteConfig(
            role=role,
            primary=self._profile_config(primary, expected_type=expected_type),
            fallback=self._profile_config(fallback, expected_type=expected_type) if fallback else None,
        )

    async def _get_db_template(self, db: AsyncSession, role: str) -> ModelRequestTemplate | None:
        result = await db.execute(
            select(ModelRequestTemplate).where(
                ModelRequestTemplate.role == role,
                ModelRequestTemplate.enabled.is_(True),
                ModelRequestTemplate.deleted == 0,
            )
        )
        return result.scalars().first()

    def _profile_config(self, profile: ModelProfile, *, expected_type: str) -> ModelProfileConfig:
        """把 ORM 模型转换为运行时配置，并在这里做启用状态和类型校验。"""
        if not profile.enabled or profile.deleted:
            raise ModelConfigurationError(f"Model profile {profile.name} is disabled.")
        if profile.model_type != expected_type:
            raise ModelConfigurationError(
                f"Model profile {profile.name} type {profile.model_type} does not match {expected_type}."
            )
        return ModelProfileConfig(
            name=profile.name,
            model_type=profile.model_type,
            provider=profile.provider,
            model=profile.model,
            base_url=profile.base_url,
            api_key=decrypt_secret(profile.encrypted_api_key),
            timeout_seconds=profile.timeout_seconds,
            temperature=profile.temperature,
            dimensions=profile.dimensions,
            config=profile.config or {},
        )

    def _fallback_route(self, role: str, *, expected_type: str) -> ModelRouteConfig:
        """构建内置 mock fallback 路由，保证空库启动和测试无需真实模型配置。"""
        if expected_type == "embedding":
            profile = ModelProfileConfig(
                name="mock_embedding",
                model_type="embedding",
                provider="mock",
                model="mock-hash-v1",
                base_url=None,
                api_key=None,
                timeout_seconds=60.0,
                temperature=None,
                dimensions=settings.embedding_dimensions,
                config={},
            )
        else:
            profile = ModelProfileConfig(
                name="mock_llm",
                model_type="chat",
                provider="mock",
                model="mock-a-plus-v1",
                base_url=None,
                api_key=None,
                timeout_seconds=60.0,
                temperature=0.2,
                dimensions=None,
                config={},
            )
        if expected_type == "image":
            profile = ModelProfileConfig(
                name="mock_image",
                model_type="image",
                provider="mock",
                model="mock-image-v1",
                base_url=None,
                api_key=None,
                timeout_seconds=60.0,
                temperature=None,
                dimensions=None,
                config={},
            )
        return ModelRouteConfig(role=role, primary=profile)

    def _fallback_template(self, role: str) -> ModelRequestTemplate:
        """构建内置默认模板，保证没有数据库模板时业务仍可运行。"""
        if role == "image_prompt":
            return ModelRequestTemplate(
                role=role,
                name="default_image_prompt",
                version="v1",
                system_prompt="You write image prompts for Amazon A+ modules. Return only JSON with an image_prompts array.",
                user_template="{payload}",
                response_contract="ImagePromptResponse",
                enabled=True,
            )
        return ModelRequestTemplate(
            role=role,
            name="default_a_plus_content",
            version="v1",
            system_prompt="You generate Amazon A+ content drafts. Return only JSON with a content_modules array.",
            user_template="{payload}",
            response_contract="APlusContentResponse",
            enabled=True,
        )
