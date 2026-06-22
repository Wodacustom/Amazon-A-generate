"""模型注册表。"""

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.model_config import ModelConfigRepository, ModelProfileConfig, ModelRouteConfig, RenderedPrompt


class ModelRegistry:
    """管理所有可用模型配置和模板。

    Registry 只负责读取和整理配置，不直接创建客户端或发起网络请求。
    """

    def __init__(self, repository: ModelConfigRepository | None = None) -> None:
        self.repository = repository or ModelConfigRepository()

    async def get_route(self, db: AsyncSession | None, role: str, *, expected_type: str) -> ModelRouteConfig:
        """读取业务 role 对应的主/备模型配置。"""
        return await self.repository.get_route(db, role, expected_type=expected_type)

    async def get_profile(self, db: AsyncSession, profile_id: int, *, expected_type: str) -> ModelProfileConfig:
        """读取单个模型档案配置。"""
        return await self.repository.get_profile(db, profile_id, expected_type=expected_type)

    async def render_prompt(self, db: AsyncSession | None, role: str, request: BaseModel) -> RenderedPrompt:
        """读取数据库模板，并用 Pydantic 请求对象渲染最终 messages。"""
        return await self.repository.render_prompt(db, role, request)
