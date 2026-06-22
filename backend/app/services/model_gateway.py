"""兼容旧导入的模型服务入口。"""

from app.services.model_config import ModelConfigurationError
from app.services.models import FallbackExecutor, ModelClient, ModelClientFactory, ModelRegistry, ModelRouter, ModelService

ModelGateway = ModelService

__all__ = [
    "FallbackExecutor",
    "ModelClient",
    "ModelClientFactory",
    "ModelConfigurationError",
    "ModelGateway",
    "ModelRegistry",
    "ModelRouter",
    "ModelService",
]
