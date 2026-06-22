"""模型客户端工厂。"""

from app.services.model_config import ModelConfigurationError, ModelProfileConfig
from app.services.models.adapters import GeminiAdapter, MockAdapter, NewAPIAdapter, OpenAIAdapter, QwenAdapter, VLLMAdapter
from app.services.models.types import ModelClient


class ModelClientFactory:
    """按 provider 创建模型客户端。

    新增供应商时只需要新增 Adapter，并在这里注册 provider 到 Adapter 的映射。
    """

    def create(self, profile: ModelProfileConfig) -> ModelClient:
        provider = profile.provider.lower()
        if provider == "mock":
            return MockAdapter(profile)
        if provider in {"openai", "openai_compatible"}:
            return OpenAIAdapter(profile)
        if provider == "qwen":
            return QwenAdapter(profile)
        if provider == "gemini":
            return GeminiAdapter(profile)
        if provider == "vllm":
            return VLLMAdapter(profile)
        if provider == "newapi":
            return NewAPIAdapter(profile)
        raise ModelConfigurationError(f"Unsupported model provider: {profile.provider}")
