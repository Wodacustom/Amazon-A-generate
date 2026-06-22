"""模型路由器。"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.model_config import ModelRouteConfig
from app.services.models.registry import ModelRegistry


class ModelRouter:
    """判断业务场景该用哪个模型。

    Router 只理解业务 role，不关心厂商协议；具体 profile 由 Registry 提供。
    """

    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()

    async def route(self, db: AsyncSession | None, role: str, *, expected_type: str) -> ModelRouteConfig:
        """返回 role 对应的主模型和可选备用模型。"""
        return await self.registry.get_route(db, role, expected_type=expected_type)
