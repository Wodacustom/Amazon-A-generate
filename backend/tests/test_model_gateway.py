"""模型服务测试。"""

import asyncio

import pytest

from app.core.config import settings
from app.services.model_config import ModelConfigurationError, ModelProfileConfig
from app.services.models import ModelClientFactory, ModelService
from app.services.models.adapters import NewAPIAdapter, QwenAdapter, VLLMAdapter


def test_mock_model_service_returns_stable_embedding_dimension():
    """验证 mock embedding 维度和配置一致。"""
    service = ModelService()

    first = asyncio.run(service.embed_query("portable grinder"))
    second = asyncio.run(service.embed_query("portable grinder"))

    assert first == second
    assert len(first) == settings.embedding_dimensions == 1536


def test_mock_model_service_parses_chat_json():
    """验证 mock LLM 路径可返回 JSON 对象。"""
    service = ModelService()

    payload = asyncio.run(service.chat_json([{"role": "user", "content": "hello"}]))

    assert payload["summary"] == "Mock model response."
    assert payload["prompt_digest"]


def test_openai_compatible_llm_requires_base_url(monkeypatch):
    """真实 LLM provider 缺配置时应给出明确错误。"""
    monkeypatch.setattr(settings, "llm_provider", "openai_compatible")
    monkeypatch.setattr(settings, "llm_base_url", None)
    monkeypatch.setattr(settings, "llm_api_key", None)

    with pytest.raises(ModelConfigurationError, match="LLM_BASE_URL"):
        asyncio.run(ModelService().chat_text([{"role": "user", "content": "hello"}]))


def test_model_client_factory_routes_openai_compatible_adapters():
    """验证工厂能创建常见 OpenAI-compatible 厂商 adapter。"""
    factory = ModelClientFactory()

    assert isinstance(factory.create(_profile("qwen")), QwenAdapter)
    assert isinstance(factory.create(_profile("vllm")), VLLMAdapter)
    assert isinstance(factory.create(_profile("newapi")), NewAPIAdapter)


def _profile(provider: str) -> ModelProfileConfig:
    return ModelProfileConfig(
        name=f"{provider}_profile",
        model_type="chat",
        provider=provider,
        model="demo",
        base_url="http://127.0.0.1/v1",
        api_key="secret",
        timeout_seconds=60,
        temperature=0.2,
        dimensions=None,
        config={},
    )
